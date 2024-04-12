% Gloe documentation master file, created by
% sphinx-quickstart on Tue Dec 12 06:33:16 2023.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Let Gloe help you

Gloe (pronounced /ɡloʊ/, like "glow") is a general purpose library made to help developers create, maintain, document and test operations and data flows. It can be used in data science and machine learning pipelines as well as in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not expected to be used in the entire application, let alone replace any existing library, it was built to be integrated with other tools and to be implemented where the code complexity may be higher than expected.

## Motivation

Software development has lots of patterns and good practices related to the code itself, like how to document, test, structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a well succeed software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artefacts and in a well-written code.

When a developer writes a code, he/she is telling a story to the next person who will read or/and refactor it. Depending on the quality of this code, this story could be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software may take a long time to clearly understand the narrative, or it will simply give up, leaving as it is.

Gloe comes to turn this story coherent, logically organized and easy to follow. This is done by dividing the code into concise steps with an unambiguous responsibility and explicit interface. Then, Gloe allows you to connect these steps, making it clear how they can work together and where you need to make changes when doing some refactoring. Therefore, you will be able to quickly visualize all the story told and improve it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implements this approach using functional programming and strong typing concepts.

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