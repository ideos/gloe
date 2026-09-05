# Quality contracts

- **QUAL-001:** Python 3.12+; verify supported released runtimes 3.12, 3.13 and 3.14. No sync/async or arity-specific public transformer variants.
- **QUAL-002:** Test with released mypy 2.3.1, with explicit bundled plugin configuration. Check source, positive assertions and intended negative diagnostic locations separately. Missing plugin configuration must not silently approve composition through Any.
- **QUAL-003:** Reject unknown stage outputs and erased signatures at composition boundaries. Runtime validates construction shape, configuration binding and validator results. Static annotations are not automatic runtime value/schema validation.
- **QUAL-004:** Execution must support long chains without recursion proportional to chain length, safe concurrent reuse, deterministic ordered results and structured cancellation cleanup.
- **QUAL-005:** Prefer fewer runtime modules and public names to compatibility layers. Keep consumer business algorithms in application functions. Test distinct real workflow contracts rather than repetitive input combinations alone.
