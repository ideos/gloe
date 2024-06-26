New Features
- 🚀 Gloe now supports an arbitrary number of transformers in a graph!
- 🔄 Async versions of each transformer from the `gloe.collection` package have been added: `FilterAsync`, `MapAsync`, and `MapOverAsync`.
- 🖼️ Added `.to_image()` and `.to_dot()` methods to transformer instances.
- 🔀 Conditional flows can now handle async transformers at any point.
- 🛠️ Introduced the `gloe.gateways` package with parallel and sequential gateways.
- 📊 Improved plotting features: support for subgraphs and better formatting of complex types.

Deprecations
- ⚠️ The `.export()` method for transformers is now deprecated in favor of the `.to_dot()` method.
- ⚠️ The `forward_incoming` utility is now deprecated in favor of the `attach` utility.

Documentation
- 📚 Adding many examples of usage with other famous Python libraries.
- 📝 Introducing Gloe patterns.
- 🔍 Exploring advanced use cases.

Tests
- ✅ Achieved 100% test coverage.
- 🧪 Improved tests packages structure.

Dependencies
- 🔗 Gloe now only depends on `typing_extensions`. `networkx` is no longer necessary.
