from abc import ABC, abstractmethod
from inspect import Signature
from typing import Type, TypeVar, Optional, Callable

from gloe.base_transformer import BaseTransformer, _In, _Out

_Self = TypeVar("_Self", bound="_GloeTransformer")


class _GloeTransformer(BaseTransformer[_In, _Out], ABC):
    """
    An intermediate abstract class that holds the common logic for both sync and async
    transformers, reducing code duplication.
    """

    @property
    @abstractmethod
    def _transform_method_name(self) -> str:
        """The name of the method that performs the transformation."""
        ...

    @property
    @abstractmethod
    def _concrete_class(self) -> Type[_Self]:
        """The concrete class of the transformer (e.g., Transformer or AsyncTransformer)."""
        ...

    def signature(self) -> Signature:
        return self._signature(self._concrete_class, self._transform_method_name)

    def __repr__(self):
        if len(self) == 1:
            return (
                f"{self.input_annotation}"
                f" -> ({self.label})"
                f" -> {self.output_annotation}"
            )

        return (
            f"{self.input_annotation}"
            f" -> ({len(self)} transformers omitted)"
            f" -> {self.output_annotation}"
        )

    def copy(
        self: _Self,
        transform: Optional[Callable[[_Self, _In], _Out]] = None,
        regenerate_instance_id: bool = False,
        force: bool = False,
    ) -> _Self:
        return self._copy(
            transform,
            regenerate_instance_id,
            self._transform_method_name,
            force,
        )
