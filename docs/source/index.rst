.. Gloe documentation master file, created by
   sphinx-quickstart on Tue Jan 24 19:22:53 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Let Gloe help you
=================

Gloe is a general purpose library made to help developers to create, maintain, document and test operational and data flows. It can be used in data science and machine learning pipelines as well in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not thought to be used in the entire application even less replacing any existing library, it was built to be integrated with other tools and to be implemented where the code complexity can be bigger than the desired.

Gloe's paradigm
---------------

The main idea behind Gloe is constraint the implementation of a specific flow into a formalized and type-safe pipeline (or execution graph). Every piece (or node) of this pipeline is responsible to transform its input into the input of the next piece, composing a sequential execution process. No code of this flow can be executed out of these pieces. Each node of a graph is called Transformer.

.. code-block:: text
   :caption: Basic structure of a Graph

   (type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> ... -> (type X)

.. note::
   Type A is called **input type** and type X is called **output type** of the graph.

A transformer must have an atomic and well-defined responsibility. As we will see later, implement a Transformer is a ridiculously easy task, so have many of them is not a problem. Keep it simple, make it easier to understand, document and test!

Lightness
`````````
Gloe is a lightweight library, it is not a development environment nor an engine and nor even a heavy framework. It was built much more on top of **strong concepts** than an exhausting amount of code.

Its dependencies are only other python libraries, nothing external is required.


Type-safety
```````````
Gloe was implemented to be completely type-safe. It means, when using Gloe, you must to provided all the type hints of the created transformers, which can be summed up in its input and output types. Using these definitions, Gloe can warn about a malformed graph right away in the IDE and make precise inferring of extremely complex types.

For example, consider the bellow Transformer:

.. code-block:: text

   (type A) -> [MyTransformer] -> (type B)

The next transformer that can be appended to `MyTransformer` must have the following signature:

.. code-block:: text

   (type B) -> [NextTransformer] -> (some type C)

That is, the output type of `MyTransformer` must be the same as the input of `NextTransformer`. When building your graphs, you will know about any problem with types immediately.

.. note::
   The representation of a transformer with its name and types is called **signature**.

To perform this kind of behavior, Gloe uses the most recent and sophisticated features of `Python typing library <https://docs.python.org/3/library/typing.html>`_.

Immutability
````````````

An important concept adopted by Gloe is immutability. Every time a Transformer is instantiated and appended as a next step of an existing one, a new Transformer is created, merging the internal operations of both transformers sequentially.

.. code-block:: text
   :caption: Immutability of transformers

   (type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> (type C)

   Above graph is in fact this:

   (type A) -> [Transformer 1 and 2] -> (type C)

It means every time we talked about a graph we was talking about a Transformer too! A graph represents a Transformer that merge the operations of its last node with the operations of the previous Transformer, recursively:

.. code-block:: text
   :caption: Graph is a Transformer (intermediate types were omitted for simplicity)

                                    +--------- Transformer [ ... [[1 2] 3] ... N] --------+
                                    |                                                     |
                                    |                                                     |
                                    |                                                     |
                     +------ Transformer [[1 2] 3] -----+                                 |
                     |                                  |                                 |
         +-- Transformer [1 2] --+                      |                                 |
         |                       |                      |                                 |
   [Transformer 1]   ->   [Transformer 2]   ->   [Transformer 3]   ->   ...   ->   [Transformer N]

.. important::
   To make easy our communication in this documentation, we will continue to call the sequence of transformers as a **graph** and any range of this sequence as a **subgraph**.

Non-linearity
`````````````

The term graph is motivated by the non-linearity characteristic of some flows. A Transformer can pass its data to more than one posterior transformers:


.. code-block:: text
   :caption: Graph non-linearity

   [Transformer 1]   -+->   [Transformer 2]   ->   [Transformer 3]   -+
                      |                                               |
                      +->   [Transformer 4]   ->   [Transformer 5]   -+->   [Transformer 6]

Any branch or ramification (transformers 2 and 3 or transformers 4 and 5 in above example) can have its own input and output types and it can be of any length and including others ramifications.



Concepts
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
