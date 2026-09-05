# Philosophy

Gloe is a notation for a typed data flow. A small function says what one step
does; `>>` says which result feeds the next step; a tuple says which independent
steps receive the same value. The graph makes those relationships inspectable.

The library stays small by leaving algorithms, loops, resource ownership, and
domain state in ordinary Python. A pipeline can connect those pieces without
silently moving work to another thread, sharing invocation state, or inventing
a cache.

Explicit data flow also makes agent-authored code easier to review. Ambiguous
input anchors, tuple spreading, configuration, and snapshots have visible
syntax. The mypy plugin checks the composition edges, while runtime validators
check the values that static typing cannot describe.
