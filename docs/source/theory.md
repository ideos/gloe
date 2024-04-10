# Gloe's theory

The main idea behind Gloe is constraining the implementation of a specific flow into a formalized and type-safe pipeline (or execution graph). Every piece (or node) of this pipeline is responsible for transforming its input into the input of the next piece, thereby composing a sequential execution process. No code from this flow can be executed outside these pieces, and each node in the graph is called a Transformer.

Basic structure of a Graph:
``` 
(type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> ... -> (type X)
```
```{admonition} Naming things
:class: seealso
Type A is called **incoming type** and type X is called **outcome type** of
the graph.
```


A transformer must have an atomic and well-defined responsibility. As we will see later, implementing a Transformer is an exceptionally straightforward task, so having many of them is not problematic. Keep it simple, hence making it easier to understand, document, and test!


## Lightness

Gloe is a lightweight library, it is not a development environment, an engine, or even a heavy framework; instead, it was built more on the basis of **strong concepts** than on an exhaustive amount of code.

Its dependencies are only other python libraries, nothing external is required.

## Type-safety

Gloe was implemented to be completely type-safe. This means that when using Gloe, you must provide all the necessary type hints of the created transformers, which can be summed up in its incoming and outcome types. Using these definitions, Gloe can warn about a malformed graph right away in the IDE and make precise inferring of extremely complex types.

For example, consider the below Transformer:

``` text
(type A) -> [MyTransformer] -> (type B)
```

The next transformer that can be appended to `MyTransformer`
must have the following signature:

``` text
(type B) -> [NextTransformer] -> (some type C)
```

That is, the outcome type of `MyTransformer` must be the same as the incoming type of `NextTransformer`. When building your graphs, you will know about any problem with types immediately.

```{admonition} Naming things
:class: seealso
The representation of a transformer with its name and types is called
**signature**.
```

To perform this kind of behavior, Gloe uses the most recent and
sophisticated features of [Python typing
library](https://docs.python.org/3/library/typing.html).

## Immutability

An important concept adopted by Gloe is immutability. Every time a
Transformer is instantiated and appended as a next step of an existing
one, a new Transformer is created, merging the internal operations of
both transformers sequentially.

```
(type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> (type C)

Above graph is in fact this:

(type A) -> [Transformer 1 and 2] -> (type C)
```

This means that every time we talk about a graph, we are also referring to a Transformer! A graph represents a Transformer that merge the
operations of its last node with the operations of the previous
Transformer, recursively.

**Graph is a Transformer** (intermediate types were omitted for simplicity):
```
                                 +--------- Transformer [ ... [[1 2] 3] ... N] --------+
                                 |                                                     |
                                 |                                                     |
                                 |                                                     |
                  +------ Transformer [[1 2] 3] -----+                                 |
                  |                                  |                                 |
      +-- Transformer [1 2] --+                      |                                 |
      |                       |                      |                                 |
[Transformer 1]   ->   [Transformer 2]   ->   [Transformer 3]   ->   ...   ->   [Transformer N]
```
```{admonition} Naming things
:class: seealso
To make easy our communication in this documentation, we will continue
to call the sequence of transformers as a **graph** or **pipeline**.
```

## Non-linearity

The term graph is motivated by the non-linearity characteristic of some
flows. A Transformer can pass its data to more than one posterior
transformers:

```
[Transformer 1]   -+->   [Transformer 2]   ->   [Transformer 3]   -+
                   |                                               |
                   +->   [Transformer 4]   ->   [Transformer 5]   -+->   [Transformer 6]
```

Any branch or ramification (transformers 2 and 3 or transformers 4 and 5 in above example) can have its own output types, and it can be of any length and including others ramifications.


## Conclusion
In summary, Gloe presents a sophisticated yet accessible framework designed to streamline the implementation of complex workflows through a type-safe, immutable, and lightweight pipeline architecture. At its core, Gloe emphasizes simplicity, modularity, and clarity by encapsulating transformation logic within discrete, well-defined units called Transformers. This design philosophy not only promotes ease of use and development efficiency but also enhances the maintainability and scalability of software solutions.

In essence, Gloe embodies a set of strong conceptual foundations that empower developers to build robust, efficient, and flexible pipelines for data transformation and processing. By abstracting away the complexities associated with graph-based execution models and focusing on simplicity and strong typing, Gloe sets a new standard for software architecture within the Python ecosystem. Whether for small-scale projects or large-scale enterprise applications, Gloe offers a compelling solution for those seeking to implement streamlined, type-safe workflows with minimal overhead and maximum efficiency.