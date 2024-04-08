% Gloe documentation master file, created by
% sphinx-quickstart on Tue Dec 12 06:33:16 2023.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Let Gloe help you

Gloe (pronounced /ɡloʊ/, like "glow") is a general purpose library made to help developers to create, maintain, document and test operational and data flows. It can be used in data science and machine learning pipelines as well in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not thought to be used in the entire application even less replacing any existing library, it was built to be integrated with other tools and to be implemented where the code complexity can be bigger than the desired.

## Motivation

The software development has a lot of patterns and good practices related to the code itself, like how to document, to test, to structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a well succeed software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artefacts and in a well-written code.

When a developer writes a code, he/she is telling a story to the next person who will read or/and refactor it. Depending on the quality of this code, this story could be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software will take a long time to understand the narrative and make it clear, or it will give up and leave it as it is.

Gloe comes to turn this story coherent, logically organized and easy to follow. This intends to be done dividing the code into concise steps with an unambiguous responsibility and explicit interface. Then, Gloe allow you to connect these steps, making clear how they can work together and where you need to make changes when doing some refactoring. Therefore, you will be able to quickly visualize all the story told and improve it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implemented this approach using functional programming and strong typing concepts.

### Gloe is not a workflow orchestrator

Currently, Gloe has not a scheduler backend like [Air Flow](https://airflow.apache.org/) or others solutions. It was built to help development. The graph structure we will see in the next sections is responsible to make the code [more flat and hence readable](https://en.wikibooks.org/wiki/Computer_Programming/Coding_Style/Minimize_nesting), but not to execute tasks in a dedicated environment. In terms of execution time or scalability, Gloe does not improve anything.

## Installing

```shell
pip install gloe
```

```{toctree}
:caption: 'Contents'
:maxdepth: 3
:hidden:

theory
getting-started/index
limitations
```

```{toctree}
:caption: 'Development'
:maxdepth: 3

gloe
```