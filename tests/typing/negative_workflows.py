"""Reject invalid application wiring at its source, before execution."""

from collections.abc import Awaitable, Callable
import gloe
from tests.scenarios import (
    Compensation,
    Document,
    ImportBatch,
    Indicator,
    Kilometers,
    Query,
    Reconciliation,
    Session,
    conserved,
    insert_rows,
    reconcile,
    replicate,
    run_indicator,
    validate_rows,
    within_budget,
)

# Configured factories retain application-level nominal units and dependencies.
# Rejected: wrong unit
gloe.transformer(within_budget)(limit=Kilometers(1))  # reject: wrong_unit

# Rejected: wrong resource
gloe.transformer(insert_rows)(session="connection")  # reject: wrong_resource

# Rejected: index contract
gloe.transformer(reconcile)(
    index={"invoice": "id"}, exact=True  # reject: index_contract
)

# Rejected: generic factory config
gloe.transformer(replicate)(count="twice")  # reject: generic_factory_config


def wrong_allocation(value: Compensation) -> str:
    return str(value.cents)


# Rejected: monetary validator result
gloe.ensure(changes=conserved)(wrong_allocation)  # reject: monetary_validator_result


def source_indicators(query: Query) -> list[Callable[[Query], str]]:
    return []


run = gloe.transformer(run_indicator)(query=Query(1))
# Rejected: async registry signature
gloe.input() >> source_indicators >> gloe.map(run)  # reject: async_registry_signature


def load_document(query: Query) -> Document:
    return Document("name", str(query.amount))


def store_batch(batch: ImportBatch) -> ImportBatch:
    return batch


# Rejected: incompatible process phases
gloe.input() >> load_document >> store_batch  # reject: incompatible_process_phases

importing = gloe.input() >> validate_rows
# Rejected: wrong pipeline entry
importing.sync(Compensation(10, 2))  # reject: wrong_pipeline_entry


async def load_indicator(query: Query) -> Indicator:
    return Indicator("sales", query.amount)


def use_query(query: Query) -> int:
    return query.amount


# Rejected: resolved result is Indicator
gloe.input() >> load_indicator >> use_query  # reject: resolved_result_is_indicator


def consume_session(session: Session) -> Reconciliation:
    return Reconciliation(())


# Rejected: incompatible inferred branches
gloe.input() >> (  # reject: incompatible_inferred_branches
    load_indicator,
    consume_session,
)


def check_number(value: int) -> None:
    pass


def keep_future(value: Awaitable[int]) -> Awaitable[int]:
    return value


# Rejected: input awaitable remains data
gloe.ensure(incoming=check_number)(keep_future)  # reject: input_awaitable_remains_data
