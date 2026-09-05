"""Mypy support for Gloe's deliberately small callable runtime.

The runtime keeps its annotations useful to ordinary checkers, but a pipeline
edge is a higher-order operation: the type of the next callable has to be
checked against the value produced by the previous edge.  This plugin asks
mypy's own call checker to perform that operation at each ``>>`` expression,
then rebuilds the two-parameter ``Transformer`` type with the resolved result.

The plugin targets the mypy minor release used by the project.  Checker plugin
APIs are not a cross-checker extension standard, so the runtime remains usable
without this module; the ``_GloeMypyPluginRequired`` annotation intentionally
makes composition fail closed when the plugin is not configured.

``TypeGuard`` and ``TypeIs`` are represented by mypy as ``TypeGuardedType``.
When mypy exposes a narrowed type that is a subtype of the collection element,
``filter`` carries that type into its list result.  If a checker version does
not expose the narrowing, the safe fallback is the original element type.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple, Union

from mypy.maptype import map_instance_to_supertype
from mypy.nodes import (
    ARG_NAMED,
    ARG_NAMED_OPT,
    ARG_POS,
    ARG_OPT,
    ARG_STAR,
    ARG_STAR2,
    CallExpr,
    Expression,
    MemberExpr,
    TempNode,
)
from mypy.plugin import FunctionContext, MethodContext, MethodSigContext, Plugin
from mypy.subtypes import is_subtype
from mypy.typeops import get_type_vars
from mypy.types import (
    AnyType,
    CallableType,
    Instance,
    NoneType,
    Overloaded,
    Parameters,
    TupleType,
    Type,
    TypeGuardedType,
    TypeType,
    TypedDictType,
    UnionType,
    get_proper_type,
)

_TRANSFORMER = "gloe._core.Transformer"
_INPUT = "gloe._core.input"
_INFER_INPUT = "gloe._core._InferInput"
_ENSURER = "gloe._validation._Ensurer"
_FUNCTIONS = "gloe._functions."
_AWAITABLE_NAMES = {
    "typing.Awaitable",
    "collections.abc.Awaitable",
}
_BOOL = "builtins.bool"
_LIST = "builtins.list"
_TUPLE = "builtins.tuple"
_ITERABLE_NAMES = {
    "typing.Iterable",
    "collections.abc.Iterable",
}


def _is_instance(value: Type, fullname: str) -> bool:
    proper = get_proper_type(value)
    return isinstance(proper, Instance) and proper.type.fullname == fullname


def _base_instance(value: Type) -> Optional[Tuple[Instance, Instance]]:
    """Return ``(Transformer base, mapped instance)`` for a pipeline value."""

    proper = get_proper_type(value)
    if not isinstance(proper, Instance):
        return None
    for info in proper.type.mro:
        if info.fullname == _TRANSFORMER:
            base = Instance(info, [])
            return base, map_instance_to_supertype(proper, info)
    return None


def _transformer_parts(value: Type) -> Optional[Tuple[Instance, Type, Type]]:
    mapped = _base_instance(value)
    if mapped is None:
        return None
    base, instance = mapped
    if len(instance.args) != 2:
        return None
    return base, instance.args[0], instance.args[1]


def _contains_unknown(value: Type, seen: Optional[set[int]] = None) -> bool:
    """Reject Any and erased callable signatures at a checked edge.

    Type variables and ParamSpecs are intentionally left alone.  Mypy's call
    checker specializes them when the edge is invoked, which is what lets
    generic functions, callable objects, overloads, and partials retain their
    normal inference behavior.
    """

    proper = get_proper_type(value)
    visited = set() if seen is None else seen
    identity = id(proper)
    if identity in visited:
        return False
    visited.add(identity)

    if isinstance(proper, AnyType):
        return True
    if isinstance(proper, CallableType) and proper.is_ellipsis_args:
        return True

    children: List[Type] = []
    if isinstance(proper, UnionType):
        children = list(proper.items)
    elif isinstance(proper, TupleType):
        children = list(proper.items)
    elif isinstance(proper, Instance):
        children = list(proper.args)
    elif isinstance(proper, CallableType):
        children = [*proper.arg_types, proper.ret_type]
    elif isinstance(proper, Parameters):
        children = list(proper.arg_types)
    elif isinstance(proper, Overloaded):
        children = list(proper.items)
    elif isinstance(proper, TypedDictType):
        children = list(proper.items.values())
    elif isinstance(proper, TypeType):
        children = [proper.item]
    return any(_contains_unknown(child, visited) for child in children)


def _is_erased_callable(value: Type) -> bool:
    proper = get_proper_type(value)
    if isinstance(proper, CallableType):
        return proper.is_ellipsis_args
    if isinstance(proper, Overloaded):
        return any(_is_erased_callable(item) for item in proper.items)
    return False


def _is_erased_partial(value: Type) -> bool:
    proper = get_proper_type(value)
    if not isinstance(proper, Instance) or proper.type.fullname != "functools.partial":
        return False
    attributes = getattr(proper, "extra_attrs", None)
    return attributes is None or "__mypy_partial" not in attributes.attrs


def _awaitable_item(value: Type) -> Optional[Type]:
    proper = get_proper_type(value)
    if not isinstance(proper, Instance):
        return None
    for info in proper.type.mro:
        if info.fullname in _AWAITABLE_NAMES:
            mapped = map_instance_to_supertype(proper, info)
            if mapped.args:
                return mapped.args[0]
    return None


def _resolved(value: Type) -> Type:
    """Remove one returned Awaitable layer, preserving nested data."""

    proper = get_proper_type(value)
    if isinstance(proper, UnionType):
        return UnionType.make_union([_resolved(item) for item in proper.items])
    item = _awaitable_item(proper)
    return item if item is not None else value


def _is_identity(value: Type) -> bool:
    proper = get_proper_type(value)
    if not isinstance(proper, Instance) or proper.type.fullname != _INPUT:
        return False
    return len(proper.args) == 1 and _is_instance(proper.args[0], _INFER_INPUT)


def _call(
    ctx: Union[FunctionContext, MethodContext],
    function: Type,
    arguments: Sequence[Type],
) -> Type:
    """Run mypy's normal call checker against a synthetic expression."""

    callee = TempNode(function)
    callee.set_line(ctx.context)
    values: List[Expression] = []
    for argument in arguments:
        value = TempNode(argument)
        value.set_line(ctx.context)
        values.append(value)
    expression = CallExpr(
        callee,
        values,
        [ARG_POS] * len(values),
        [None] * len(values),
    )
    expression.set_line(ctx.context)
    return ctx.api.get_expression_type(expression)


def _signature(
    ctx: Union[FunctionContext, MethodContext], value: Type
) -> Optional[Union[CallableType, Overloaded]]:
    proper = get_proper_type(value)
    if isinstance(proper, (CallableType, Overloaded)):
        return proper
    if isinstance(proper, Instance):
        access = MemberExpr(TempNode(value), "__call__")
        access.set_line(ctx.context)
        called = get_proper_type(ctx.api.get_expression_type(access))
        if isinstance(called, (CallableType, Overloaded)):
            return called
    return None


def _first_positional(signature: CallableType) -> Optional[Type]:
    for argument, kind in zip(signature.arg_types, signature.arg_kinds):
        if kind in (ARG_POS, ARG_OPT):
            return argument
    return None


def _argument(
    ctx: FunctionContext,
    name: str,
    position: int,
) -> Optional[Type]:
    """Find a function argument by keyword name, with positional fallback."""

    for index, arg_names in enumerate(ctx.arg_names):
        if name in arg_names and ctx.arg_types[index]:
            return ctx.arg_types[index][0]
    if position < len(ctx.arg_types) and ctx.arg_types[position]:
        return ctx.arg_types[position][0]
    return None


def _copy_callable(function: CallableType, **changes: object) -> CallableType:
    # ``copy_modified`` is an extension point of mypy's internal Type API.  It
    # is stable for the pinned release and keeps all unmodified generic scope,
    # fallback, and signature metadata intact.
    return function.copy_modified(**changes)  # type: ignore[arg-type]


def _partition_one(ctx: FunctionContext, function: CallableType) -> CallableType:
    if any(kind in (ARG_STAR, ARG_STAR2) for kind in function.arg_kinds):
        ctx.api.fail(
            "Configured transformers require explicit input and configuration "
            "parameters",
            ctx.context,
        )
        return function

    config_indexes = [
        index
        for index, kind in enumerate(function.arg_kinds)
        if kind in (ARG_NAMED, ARG_NAMED_OPT)
    ]
    input_indexes = [
        index
        for index, kind in enumerate(function.arg_kinds)
        if kind not in (ARG_NAMED, ARG_NAMED_OPT)
    ]
    config_ids = {
        variable.id
        for index in config_indexes
        for variable in get_type_vars(function.arg_types[index])
    }
    outer_variables = [
        variable for variable in function.variables if variable.id in config_ids
    ]
    inner_variables = [
        variable for variable in function.variables if variable.id not in config_ids
    ]
    configured = _copy_callable(
        function,
        arg_types=[function.arg_types[index] for index in input_indexes],
        arg_kinds=[function.arg_kinds[index] for index in input_indexes],
        arg_names=[function.arg_names[index] for index in input_indexes],
        variables=inner_variables,
    )
    return _copy_callable(
        function,
        arg_types=[function.arg_types[index] for index in config_indexes],
        arg_kinds=[function.arg_kinds[index] for index in config_indexes],
        arg_names=[function.arg_names[index] for index in config_indexes],
        ret_type=configured,
        variables=outer_variables,
    )


def _partition_factory(ctx: FunctionContext) -> Type:
    if not ctx.arg_types or not ctx.arg_types[0]:
        return ctx.default_return_type
    function = get_proper_type(ctx.arg_types[0][0])
    if isinstance(function, CallableType):
        return _partition_one(ctx, function)
    if isinstance(function, Overloaded):
        return Overloaded([_partition_one(ctx, item) for item in function.items])
    ctx.api.fail("transformer requires one explicitly typed callable", ctx.context)
    return ctx.default_return_type


def _validate_input(ctx: FunctionContext) -> Type:
    result = get_proper_type(ctx.default_return_type)
    if isinstance(result, Instance) and _contains_unknown(result):
        ctx.api.fail(
            "Pipeline input type contains Any or an erased callable signature",
            ctx.context,
        )
    return result


def _construct_transformer(ctx: FunctionContext) -> Type:
    result = get_proper_type(ctx.default_return_type)
    if not isinstance(result, Instance) or len(result.args) != 2:
        return result
    output = _resolved(result.args[1])
    if _contains_unknown(output):
        ctx.api.fail(
            "Pipeline stage result contains Any or an erased signature; "
            "annotate or adapt it",
            ctx.context,
        )
    return result.copy_modified(args=[result.args[0], output])


def _inferred_input(
    ctx: MethodContext,
    receiver: Instance,
    node: Type,
) -> Optional[Tuple[Instance, Type, Parameters]]:
    mapped_parts = _base_instance(receiver)
    if mapped_parts is None:
        return None
    _, mapped = mapped_parts
    if not mapped.args:
        return None
    upstream = mapped.args[1] if len(mapped.args) > 1 else None
    if upstream is None or not _is_instance(upstream, _INFER_INPUT):
        return None

    proper_node = get_proper_type(node)
    nodes = list(proper_node.items) if isinstance(proper_node, TupleType) else [node]
    candidates: List[Type] = []
    for item in nodes:
        if _is_identity(item):
            continue
        signature = _signature(ctx, item)
        if signature is None:
            ctx.api.fail(
                "Cannot infer pipeline input; provide input[T]() or a concrete "
                "unary stage",
                ctx.context,
            )
            return None
        overloads = (
            signature.items if isinstance(signature, Overloaded) else [signature]
        )
        if len(overloads) != 1:
            ctx.api.fail(
                "Cannot infer pipeline input from an overloaded stage; provide "
                "input[T]()",
                ctx.context,
            )
            return None
        first = _first_positional(overloads[0])
        if (
            first is None
            or _is_erased_callable(overloads[0])
            or _contains_unknown(first)
            or get_type_vars(first)
        ):
            ctx.api.fail(
                "Cannot infer input from a generic or unknown parameter; provide "
                "input[T]()",
                ctx.context,
            )
            return None
        candidates.append(first)

    if not candidates:
        ctx.api.fail(
            "Identity-only input needs an explicit type",
            ctx.context,
        )
        return None
    compatible = [
        candidate
        for candidate in candidates
        if all(is_subtype(candidate, other) for other in candidates)
    ]
    if not compatible:
        ctx.api.fail(
            "Branch input types do not establish one compatible input; provide "
            "input[T]()",
            ctx.context,
        )
        return None
    inferred = compatible[0]
    parameters = Parameters([inferred], [ARG_POS], [None])
    return mapped, inferred, parameters


def _compose(ctx: MethodContext) -> Type:
    receiver_type = get_proper_type(ctx.type)
    if not isinstance(receiver_type, Instance):
        return ctx.default_return_type
    parts = _transformer_parts(receiver_type)
    if parts is None or not ctx.arg_types or not ctx.arg_types[0]:
        return ctx.default_return_type
    base, parameters, upstream = parts
    node = ctx.arg_types[0][0]

    if _is_instance(upstream, _INFER_INPUT):
        inferred = _inferred_input(ctx, receiver_type, node)
        if inferred is None:
            return ctx.default_return_type
        _, upstream, parameters = inferred

    proper_node = get_proper_type(node)
    nodes = list(proper_node.items) if isinstance(proper_node, TupleType) else [node]
    outputs: List[Type] = []
    for item in nodes:
        if _is_identity(item):
            outputs.append(upstream)
            continue
        if _is_erased_partial(item):
            ctx.api.fail(
                "Partial signature was erased; retain inference or use a typed adapter",
                ctx.context,
            )
        signature = _signature(ctx, item)
        if signature is not None and _is_erased_callable(signature):
            ctx.api.fail(
                "Pipeline callable signature was erased; retain its typed parameters",
                ctx.context,
            )
        result = _call(ctx, item, [upstream])
        resolved = _resolved(result)
        if _contains_unknown(resolved):
            ctx.api.fail(
                "Pipeline stage result contains Any or an erased signature; "
                "annotate or adapt it",
                ctx.context,
            )
        outputs.append(resolved)

    if isinstance(proper_node, TupleType):
        fallback = proper_node.partial_fallback
        output: Type = TupleType(outputs, fallback)
    else:
        output = outputs[0]
    return Instance(base.type, [parameters, output])


def _checked_argument_signature(ctx: MethodSigContext) -> CallableType:
    object_type = ctx.api.named_generic_type("builtins.object", [])
    return ctx.default_signature.copy_modified(arg_types=[object_type])


def _iterable_item(value: Type) -> Optional[Type]:
    proper = get_proper_type(value)
    if isinstance(proper, TupleType):
        if not proper.items:
            return None
        return UnionType.make_union(list(proper.items))
    if isinstance(proper, Instance):
        for info in proper.type.mro:
            if info.fullname in _ITERABLE_NAMES:
                mapped = map_instance_to_supertype(proper, info)
                if mapped.args:
                    return mapped.args[0]
        if proper.type.fullname in (_LIST, "builtins.tuple") and proper.args:
            return proper.args[0]
    return None


def _list(ctx: FunctionContext, item: Type) -> Instance:
    return ctx.api.named_generic_type(_LIST, [item])


def _awaitable(ctx: FunctionContext, item: Type) -> Instance:
    return ctx.api.named_generic_type("typing.Awaitable", [item])


def _replace_return(stage: Type, return_type: Type) -> Type:
    proper = get_proper_type(stage)
    if isinstance(proper, CallableType):
        return _copy_callable(proper, ret_type=return_type)
    return stage


def _predicate(ctx: FunctionContext, function: Type, item: Type) -> Optional[Type]:
    function_type = get_proper_type(function)
    guard: Optional[Type] = None
    if isinstance(function_type, CallableType):
        guard = function_type.type_is or function_type.type_guard
    # An overloaded predicate may select a non-narrowing bool overload at
    # this input type.  Without the checker’s selected overload, carrying one
    # guard across the whole union would be unsound, so retain the source item
    # type for overloaded predicates.
    result = _resolved(_call(ctx, function, [item]))
    if _contains_unknown(result):
        ctx.api.fail(
            "Predicate result contains Any or an erased signature; annotate or "
            "adapt it",
            ctx.context,
        )
        return None
    if guard is not None:
        narrowed = guard
        # TypeIs is soundly useful for filter when its target is within the
        # source element.  Keep the source type for other guard shapes.
        if not _contains_unknown(narrowed) and not get_type_vars(narrowed):
            return narrowed if is_subtype(narrowed, item) else item
    proper = get_proper_type(result)
    if isinstance(proper, TypeGuardedType):
        narrowed = proper.type_guard
        if not _contains_unknown(narrowed) and not get_type_vars(narrowed):
            return narrowed if is_subtype(narrowed, item) else item
    bool_type = ctx.api.named_generic_type(_BOOL, [])
    if not is_subtype(result, bool_type):
        ctx.api.fail("Filter and condition predicates must produce bool", ctx.context)
        return None
    return item


def _collection_factory(ctx: FunctionContext, keep_input: bool) -> Type:
    stage = get_proper_type(ctx.default_return_type)
    if not isinstance(stage, CallableType) or not stage.arg_types:
        return stage
    item = _iterable_item(stage.arg_types[0])
    function = _argument(ctx, "using", 0)
    if item is None or function is None:
        return stage
    if keep_input:
        result_item = _predicate(ctx, function, item)
    else:
        result_item = _resolved(_call(ctx, function, [item]))
        if _contains_unknown(result_item):
            ctx.api.fail(
                "Collection callback output contains Any or an erased signature",
                ctx.context,
            )
    if result_item is None:
        return stage
    return _replace_return(stage, _awaitable(ctx, _list(ctx, result_item)))


def _dynamic_factory(ctx: FunctionContext) -> Type:
    stage = get_proper_type(ctx.default_return_type)
    if not isinstance(stage, CallableType) or not stage.arg_types:
        return stage
    item_input = stage.arg_types[0]
    using = _argument(ctx, "using", 0)
    if using is None:
        return stage
    branch = _iterable_item(using)
    if branch is None:
        ctx.api.fail("Dynamic branches must be an iterable of callables", ctx.context)
        return stage
    proper_branch = get_proper_type(branch)
    branch_types = (
        list(proper_branch.items) if isinstance(proper_branch, UnionType) else [branch]
    )
    outputs: List[Type] = []
    for function in branch_types:
        if _is_erased_callable(function):
            ctx.api.fail(
                "Dynamic branch signature was erased; retain its typed parameters",
                ctx.context,
            )
        output = _resolved(_call(ctx, function, [item_input]))
        if _contains_unknown(output):
            ctx.api.fail(
                "Dynamic branch output contains Any or an erased signature",
                ctx.context,
            )
        outputs.append(output)
    if not outputs:
        return stage
    return _replace_return(
        stage, _awaitable(ctx, _list(ctx, UnionType.make_union(outputs)))
    )


def _condition_factory(ctx: FunctionContext) -> Type:
    stage = get_proper_type(ctx.default_return_type)
    if not isinstance(stage, CallableType) or not stage.arg_types:
        return stage
    item = stage.arg_types[0]
    predicate = _argument(ctx, "using", 0)
    then = _argument(ctx, "then", 1)
    otherwise = _argument(ctx, "otherwise", 2)
    if predicate is None or then is None or otherwise is None:
        return stage
    narrowed = _predicate(ctx, predicate, item)
    if narrowed is None:
        narrowed = item
    then_result = _resolved(_call(ctx, then, [narrowed]))
    otherwise_result = _resolved(_call(ctx, otherwise, [item]))
    if _contains_unknown(then_result) or _contains_unknown(otherwise_result):
        ctx.api.fail(
            "Condition branch output contains Any or an erased signature",
            ctx.context,
        )
    return _replace_return(
        stage,
        _awaitable(ctx, UnionType.make_union([then_result, otherwise_result])),
    )


def _unpack_one(ctx: FunctionContext, function: Type) -> Type:
    proper = get_proper_type(function)
    if isinstance(proper, Overloaded):
        adapted: List[CallableType] = []
        for item in proper.items:
            candidate = _unpack_one(ctx, item)
            if isinstance(candidate, Overloaded):
                adapted.extend(candidate.items)
            elif isinstance(candidate, CallableType):
                adapted.append(candidate)
            else:
                return function
        return Overloaded(adapted)
    if not isinstance(proper, CallableType):
        signature = _signature(ctx, function)
        if signature is None or isinstance(signature, Overloaded):
            ctx.api.fail("unpack requires one explicitly typed callable", ctx.context)
            return function
        proper = signature
    if proper.is_ellipsis_args or any(
        kind in (ARG_STAR, ARG_STAR2) for kind in proper.arg_kinds
    ):
        ctx.api.fail(
            "unpack requires a fixed positional callable signature", ctx.context
        )
        return proper
    positional = [
        argument
        for argument, kind in zip(proper.arg_types, proper.arg_kinds)
        if kind in (ARG_POS, ARG_OPT)
    ]
    if ARG_NAMED in proper.arg_kinds:
        ctx.api.fail(
            "unpack cannot supply keyword-only callable parameters", ctx.context
        )
        return proper
    fallback = ctx.api.named_generic_type(_TUPLE, [])
    required = sum(kind == ARG_POS for kind in proper.arg_kinds)
    optional = sum(kind == ARG_OPT for kind in proper.arg_kinds)
    adapted = []
    for count in range(required, required + optional + 1):
        tuple_type = TupleType(positional[:count], fallback)
        adapted.append(
            _copy_callable(
                proper,
                arg_types=[tuple_type],
                arg_kinds=[ARG_POS],
                arg_names=[None],
            )
        )
    if len(adapted) == 1:
        return adapted[0]
    return Overloaded(adapted)


def _unpack_factory(ctx: FunctionContext) -> Type:
    function = _argument(ctx, "function", 0)
    return (
        _unpack_one(ctx, function) if function is not None else ctx.default_return_type
    )


def _validator_group(value: Optional[Type], ctx: FunctionContext) -> TupleType:
    fallback = ctx.api.named_generic_type(_TUPLE, [])
    if value is None:
        return TupleType([], fallback)
    proper = get_proper_type(value)
    if isinstance(proper, TupleType):
        return proper
    if isinstance(proper, Instance) and proper.type.fullname in (_LIST, _TUPLE):
        return TupleType(list(proper.args), fallback)
    return TupleType([value], fallback)


def _validator_factory(ctx: FunctionContext) -> Type:
    result = get_proper_type(ctx.default_return_type)
    if not isinstance(result, Instance) or result.type.fullname != _ENSURER:
        return result
    groups = [
        _validator_group(_argument(ctx, name, index), ctx)
        for index, name in enumerate(("incoming", "outcome", "changes"))
    ]
    return result.copy_modified(args=groups)


def _group_callbacks(value: Type) -> List[Type]:
    proper = get_proper_type(value)
    if isinstance(proper, TupleType):
        return list(proper.items)
    if isinstance(proper, Instance) and proper.type.fullname in (_LIST, _TUPLE):
        return list(proper.args)
    return [value]


def _ensure_callable(ctx: MethodContext) -> Type:
    # The signature hook preserves the original callable instead of selecting
    # one overload through the generic decorator parameter.
    function = _proper_arg(ctx.arg_types)
    if isinstance(function, CallableType):
        signatures = [function]
    elif isinstance(function, Overloaded):
        signatures = list(function.items)
    else:
        ctx.api.fail("Ensurers require one explicitly typed callable", ctx.context)
        return function if function is not None else ctx.default_return_type
    ensurer = get_proper_type(ctx.type)
    if not isinstance(ensurer, Instance) or len(ensurer.args) != 3:
        return function if function is not None else ctx.default_return_type
    groups = [_group_callbacks(group) for group in ensurer.args]
    # A validator must work for every overload, not only the first signature.
    for signature in signatures:
        positional = [
            argument
            for argument, kind in zip(signature.arg_types, signature.arg_kinds)
            if kind in (ARG_POS, ARG_OPT)
        ]
        if len(positional) != 1 or any(
            kind in (ARG_STAR, ARG_STAR2) for kind in signature.arg_kinds
        ):
            ctx.api.fail("Ensurers require one positional data input", ctx.context)
            continue
        # Input awaitables remain data; only returned awaitables are normalized.
        incoming = positional[0]
        outcome = _resolved(signature.ret_type)
        validator_arguments = ([incoming], [outcome], [incoming, outcome])
        for callbacks, arguments in zip(groups, validator_arguments):
            for validator in callbacks:
                result = _call(ctx, validator, arguments)
                if not isinstance(get_proper_type(result), NoneType):
                    ctx.api.fail(
                        "Ensurer validators must synchronously return None or raise",
                        ctx.context,
                    )
    return function if function is not None else ctx.default_return_type


def _proper_arg(arguments: List[List[Type]]) -> Optional[Type]:
    for argument in arguments:
        if argument:
            return argument[0]
    return None


class GloeMypyPlugin(Plugin):
    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodSigContext], CallableType]]:
        if fullname in {
            f"{_TRANSFORMER}.__rshift__",
            f"{_INPUT}.__rshift__",
            f"{_ENSURER}.__call__",
        }:
            return _checked_argument_signature
        return None

    def get_method_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodContext], Type]]:
        if fullname in {
            f"{_TRANSFORMER}.__rshift__",
            f"{_INPUT}.__rshift__",
        }:
            return _compose
        if fullname == f"{_ENSURER}.__call__":
            return _ensure_callable
        return None

    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname == _TRANSFORMER:
            return _construct_transformer
        if fullname == _INPUT:
            return _validate_input
        if fullname == f"{_FUNCTIONS}transformer":
            return _partition_factory
        if fullname == f"{_FUNCTIONS}map":
            return lambda ctx: _collection_factory(ctx, False)
        if fullname == f"{_FUNCTIONS}filter":
            return lambda ctx: _collection_factory(ctx, True)
        if fullname == f"{_FUNCTIONS}condition":
            return _condition_factory
        if fullname in {f"{_FUNCTIONS}parallel", f"{_FUNCTIONS}sequential"}:
            return _dynamic_factory
        if fullname == f"{_FUNCTIONS}unpack":
            return _unpack_factory
        if fullname == "gloe._validation.ensure":
            return _validator_factory
        return None


def plugin(version: str) -> type[Plugin]:
    return GloeMypyPlugin
