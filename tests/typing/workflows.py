"""Exact types for real workflow shapes, using the same runtime-test functions."""

from collections.abc import Iterable
from typing import assert_type

import gloe
from tests.scenarios import (
    Analysis,
    Compensation,
    Document,
    Edge,
    ImportBatch,
    Indicator,
    IndicatorFunction,
    Meters,
    Query,
    Reconciliation,
    ReportSpec,
    RouteInputs,
    Runner,
    Session,
    assemble,
    available,
    build_report,
    conserved,
    document_body,
    enabled,
    flatten,
    group_reports,
    hot,
    insert_rows,
    load_configs,
    loaders,
    reconcile,
    replicate,
    route_inputs,
    run_indicator,
    runners,
    split_compensation,
    tokenize,
    update_invoices,
    valid_compensation,
    validate_rows,
    within_budget,
)

catalog = (ReportSpec(1, "sales"), ReportSpec(1, "rebates"))
build = gloe.transformer(build_report)(registered=frozenset({"sales", "rebates"}))
reports = gloe.input() >> gloe.filter(enabled) >> gloe.map(build) >> group_reports
reporting = (
    gloe.input()
    >> gloe.transformer(load_configs)(catalog=catalog)
    >> (reports, loaders)
    >> runners
)
assert_type(reporting, gloe.Transformer[[list[int]], list[Runner]])

exact = gloe.transformer(reconcile)(index={"exact": 10}, exact=True)
fallback = gloe.transformer(reconcile)(index={"fallback": 20}, exact=False)
reconciliation = gloe.input() >> exact >> fallback
assert_type(reconciliation, gloe.Transformer[[Reconciliation], Reconciliation])

split = gloe.ensure(incoming=valid_compensation, changes=conserved)(split_compensation)
allocation = gloe.input() >> split
assert_type(allocation, gloe.Transformer[[Compensation], tuple[int, ...]])

run = gloe.transformer(run_indicator)(query=Query(10))
indicators = gloe.input() >> gloe.map(run)
assert_type(
    indicators,
    gloe.Transformer[[Iterable[IndicatorFunction]], list[Indicator]],
)

seeds = (
    gloe.input()
    >> gloe.filter(hot)
    >> gloe.transformer(within_budget)(limit=Meters(100))
)
routing = (
    gloe.input() >> gloe.filter(available) >> (gloe.input(), seeds) >> route_inputs
)
assert_type(routing, gloe.Transformer[[Iterable[Edge]], RouteInputs])

work = gloe.input() >> document_body >> tokenize
retain_original = gloe.input() >> (gloe.input(), work) >> gloe.unpack(assemble)
assert_type(retain_original, gloe.Transformer[[Document], Analysis])


def import_pipeline(session: Session) -> gloe.Transformer[[ImportBatch], ImportBatch]:
    return (
        gloe.input()
        >> validate_rows
        >> gloe.transformer(insert_rows)(session=session)
        >> gloe.transformer(update_invoices)(session=session)
    )


flat = gloe.input[list[list[int]]]() >> flatten
assert_type(flat, gloe.Transformer[[list[list[int]]], list[int]])
repeat = gloe.transformer(replicate)(count=2)
assert_type(gloe.input[int]() >> repeat, gloe.Transformer[[int], list[int]])
assert_type(gloe.input[str]() >> repeat, gloe.Transformer[[str], list[str]])
