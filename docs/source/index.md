% Gloe documentation master file, created by
% sphinx-quickstart on Tue Dec 12 06:33:16 2023.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Let Gloe help you

Gloe (pronounced /ɡloʊ/, like "glow") is a general purpose library made to help developers to create, maintain, document and test operational and data flows. It can be used in data science and machine learning pipelines as well in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not thought to be used in the entire application even less replacing any existing library, it was built to be integrated with other tools and to be implemented where the code complexity can be bigger than the desired.

## Motivation

Software development has a lot of patterns and good practices related to the code itself, like how to document, to test, to structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a successful software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artifacts and in a well-written code.

When a developers write a code, they are telling a story to the next person who will read or/and refactor it. Depending on the code's quality, the story can be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software will take a long time to understand the narrative and make it clear, or they might give up and leave it as is.

Gloe comes to turn this story coherent, logically organized and easy to follow. This is achieved by dividing the code into concise steps with an unambiguous responsibility and explicit interface. Then, Gloe allows you to connect these steps, clarifying their collaboration and identifying necessary changes during refactoring. Thus, you can quickly understand the entire story being told and enhance it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implemented this approach using functional programming and strong typing concepts.

### Gloe is not a workflow orchestrator

Currently, unlike platforms like [Air Flow](https://airflow.apache.org/) that include scheduler backends for task orchestration, Gloe's primary purpose is to aid in development. The graph structure, which will be discussed in subsequent sections, aims to make the code [more flat and hence readable](https://en.wikibooks.org/wiki/Computer_Programming/Coding_Style/Minimize_nesting). However, it is important to note that Gloe does not offer functionalities for executing tasks in a dedicated environment, nor does it directly contribute to execution speed or scalability improvements.

## Installing

```shell
pip install gloe
```

```{toctree}
:caption: 'Contents'
:maxdepth: 3
:hidden:

Introduction <self>
theory
getting-started/index
limitations
```

```{toctree}
:caption: 'Development'
:maxdepth: 3
:hidden:

api-reference/index
```