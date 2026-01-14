# AGENTS

## General
- Target Python >= 3.10.
- Use `uv` as the default package manager and runner.
- Keep code simple and self-documenting; do not add random comments.

## Typing
- Use strong, explicit typing everywhere.
- This library is mypy-heavy; ensure all code type-checks cleanly.

## Documentation pattern
- Follow the existing docstring style used in the codebase (reST/Sphinx style).
- Prefer structured sections like `Args:`, `Returns:`, `Raises:`, `Example:`, and `See Also:` when documenting.

## Testing
- Always run the full test suite at the end of a task (use `uv`).
