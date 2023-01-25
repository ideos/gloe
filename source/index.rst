.. Gloe documentation master file, created by
   sphinx-quickstart on Tue Jan 24 19:22:53 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Gloe's paradigm
================================

Gloe is a general purpose library made to help developers to create, maintain, document and test operational and data flows. It can be used in data science and machine learning pipelines as well in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not thought to be used in the entire application even less replacing any existing library, it was built to be integrated with other tools and to be implemented where the code complexity can be bigger than the desired.

The main idea behind Gloe is constraint the implementation of a specific flow into a formalized and type-safe pipeline (or execution graph). Every piece (or node) of this pipeline is responsible to transform its input into the input of the next piece, composing a sequential execution process. No code of this flow can be executed out of these pieces. Each node of a graph is called Transformer.

.. code-block:: text
   :caption: Basic structure of a Graph

   (type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> ... -> (type X)

A transformer must have an atomic and well-defined responsibility. As we will see later, implement a Transformer is a ridiculously easy task, so have many of them is not a problem. Keep it simple, make it easier to understand, document and test!

An important concept adopted by Gloe is immutability. Every time a Transformer is instantiated and appended as a next step of an existing one, a new Transformer is created, merging the internal operations of both transformers sequentially.

.. code-block:: text
   :caption: Immutability of transformers

   (type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> (type C)

   Above graph is in fact this:

   (type A) -> [Transformer 1 and 2] -> (type C)

It means every time we talked about a graph we was talking about a Transformer too! A graph represents a Transformer that merge the operations of its last node with the operations of the previous Transformer, recursively:

.. code-block:: text
   :caption: Graph is a Transformer (intermediate types was omitted for simplicity)

                                    +----------- Transformer [[[1 2] 3] ... N] -----------+
                                    |                                                     |
                     +------ Transformer [[1 2] 3] -----+                                 |
                     |                                  |                                 |
         +-- Transformer [1 2] --+                      |                                 |
         |                       |                      |                                 |
   [Transformer 1]   ->   [Transformer 2]   ->   [Transformer 3]   ->   ...   ->   [Transformer N]



.. toctree::
   :maxdepth: 2
   :caption: Concepts:

   Transformer

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
