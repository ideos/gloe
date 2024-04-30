(philosophy)=
# Philosophy

Gloe was designed with specific guiding principles in mind. These principles are in line with [Python's Zen](https://peps.python.org/pep-0020/) and form the core of our philosophy, which is detailed in the following sections.

## Default Typing Features

Gloe emphasizes the use of Python's built-in typing features. The reason for that is we believe that it enhances reliability and developer experience without the need for external Mypy plugins with complex type systems and their own documentation.

## Explicity is Better Than Implicity

Gloe values explicitness in coding. We encourage developers to write code that speaks for itself rather than relying on hidden behaviors. This philosophy aids in making the code more readable and understandable, ensuring that operations and intentions are clear to new readers and maintainers. Transformers have an explicit interface, and must have an explicit role. When connecting many transformers in a pipeline, it is easy to quickly visualize the whole flow.

(flat-is-better-than-nested)=
## Flat is Better Than Nested

Gloe supports a flat structure in code development as opposed to deep nesting. It not only simplifies understanding and debugging but also aligns with our goal to make software logic as transparent as possible. It also mirrors the natural flow of thought on the code flow, eliminating the cognitive load that typically comes with tracing through nested structures. For that reason, a transformer must never have a call for other transformers into its logic, otherwise, in this case, the code reader will have to keep two flows in mind.

## Code Understanding Close to Business Logic

Gloe is designed to bridge the gap between complex coding structures and business logic. When implementing a complex flow, such as a data pipeline, it is common to outline the flow in a draft, considering the operations and the data flowing between them. This draft is likely the closest part to business logic. With Gloe, mapping this outlined flow into code is straightforward.

## Maximize the Maintainability

Gloe's design principles prioritize maintainability. By ensuring that the code is well-documented and logically structured, Gloe helps reduce the effort associated with ongoing maintenance. In addition, when refactoring an existing Gloe pipeline, you can change the order of complex operations only by changing the transformer's order. You can also add new operations, by just inserting a new transformer in the middle of the already present ones. By respecting the transformers interface, you can guarantee that they will work as before.
