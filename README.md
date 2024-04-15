***

<div align="center">
  <img src="https://github.com/ideos/gloe/raw/main/docs/source/_static/assets/gloe-logo.png"><br>
</div>


| |                                                                                                                                                                                                                                                             |
| --- |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Testing | [![CI - Test](https://github.com/ideos/gloe/actions/workflows/test.yml/badge.svg)](https://github.com/ideos/gloe/actions/workflows/test.yml) [![Coverage](https://codecov.io/github/ideos/gloe/coverage.svg?branch=main)](https://codecov.io/gh/ideos/gloe) |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/gloe.svg?color=%2334D058)](https://pypi.org/project/gloe) [![Supported Python versions](https://img.shields.io/pypi/pyversions/gloe.svg?color=%2334D058)](https://pypi.org/project/gloe)              |
| Meta | [![License - Apache 2.0](https://img.shields.io/pypi/l/gloe.svg?color=%2304b367)](https://github.com/ideos/gloe/blob/main/LICENSE)                                                                                                                          | 

**Documentation**: [gloe.ideos.com.br](https://gloe.ideos.com.br)

# Write a Better Python Code

Gloe (pronounced /ɡloʊ/, like "glow") is a general-purpose library made to help developers create, maintain, document, and test both operational and flow-oriented code. It is particularly useful in data science and machine learning pipelines, as well as in servers and scripts, or any area where there is a gap between the code and the logical business understanding. Gloe is not intended to be used across an entire application or to replace existing libraries. Instead, it is built to integrate with other tools and to address areas where the code complexity may be higher than expected.

## Motivation

Software development has lots of patterns and good practices related to the code itself, like how to document, test, structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a successful software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artifacts and in a well-written code.

When developers write a code, they are telling a story to the next person who will read or/and refactor it. Depending on the code's quality, this story could be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software may take a long time to clearly understand the narrative and make it clear, or they will simply give up, leaving it as is.


### How Gloe Can Help Me?

Gloe comes to turn this story coherent, logically organized and easy to follow. This is achieved by dividing the code into [concise steps](https://gloe.ideos.com.br/theory.html) with an unambiguous responsibility and explicit interface. Then, Gloe allows you to connect these steps, clarifying their collaboration and identifying necessary changes during refactoring. Thus, you can quickly understand the entire story being told and enhance it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implemented this approach using functional programming and strong typing concepts.

### Gloe is not a workflow orchestrator

Currently, unlike platforms like [Air Flow](https://airflow.apache.org/) that include scheduler backends for task orchestration, Gloe's primary purpose is to aid in development. The graph structure, which will be discussed in subsequent sections, aims to make the code [more flat and hence readable](https://en.wikibooks.org/wiki/Computer_Programming/Coding_Style/Minimize_nesting). However, it is important to note that Gloe does not offer functionalities for executing tasks in a dedicated environment, nor does it directly contribute to execution speed or scalability improvements.

## Installing

```shell
pip install gloe
```

## License

[Apache License Version 2.0](https://github.com/ideos/gloe/blob/main/LICENSE)