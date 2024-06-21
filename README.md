
<div align="center" style="margin-top: 2rem;">
  <img src="https://gloe.ideos.com.br/_static/assets/gloe-logo.png"><br>
</div>


| | | 
| ---:|----|
| Testing | [![CI - Test](https://github.com/ideos/gloe/actions/workflows/test.yml/badge.svg)](https://github.com/ideos/gloe/actions/workflows/test.yml) [![Coverage](https://codecov.io/github/ideos/gloe/coverage.svg?branch=main)](https://codecov.io/gh/ideos/gloe) |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/gloe.svg?color=%2334D058)](https://pypi.org/project/gloe) [![Anaconda Latest Release](https://anaconda.org/conda-forge/gloe/badges/version.svg)](https://anaconda.org/conda-forge/gloe) [![Supported Python versions](https://img.shields.io/pypi/pyversions/gloe.svg?color=%2334D058)](https://pypi.org/project/gloe) |
| Meta | [![License - Apache 2.0](https://img.shields.io/pypi/l/gloe.svg?color=%2304b367)](https://github.com/ideos/gloe/blob/main/LICENSE) |
| Code | [![Code quality](https://github.com/ideos/gloe/actions/workflows/code-quality.yml/badge.svg)](https://github.com/ideos/gloe/actions/workflows/code-quality.yml) [![Style](https://img.shields.io/badge/style-black-000000.svg)](https://github.com/psf/black) [![Flake8](https://img.shields.io/badge/flake8-checked-7854cc)](https://flake8.pycqa.org/) [![Mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://www.mypy-lang.org/)|

***

**Read the documentation**: [gloe.ideos.com.br](https://gloe.ideos.com.br)

**Souce code**: [github.com/ideos/gloe](https://github.com/ideos/gloe)

**FAQ**: [gloe.ideos.com.br/faq.html](https://gloe.ideos.com.br/faq.html)

***

### Table of Contents:
<!-- TOC -->
  * [Key Features](#key-features)
  * [Installing](#installing)
  * [Example](#example)
    * [Flow Steps: Transformers](#flow-steps-transformers)
    * [Maintainance](#maintainance)
    * [Type checking](#type-checking)
    * [Simple Usage](#simple-usage)
    * [Quick Documentation](#quick-documentation)
    * [Integration](#integration-)
  * [Motivation](#motivation)
    * [How Can Gloe Help Me?](#how-can-gloe-help-me)
    * [Gloe is not a workflow orchestrator](#gloe-is-not-a-workflow-orchestrator)
  * [License](#license)
<!-- TOC -->

# Your Code like a Flow

Gloe (pronounced /ɡloʊ/, like "glow") is a general-purpose library designed to guide developers in expressing their code as a **flow**. 

**Why follow this approach?** Because it ensures that Gloe can keep your Python code easy to maintain, document, and test. Gloe guides you to write code in the form of small, safely connected units, rather than relying on scattered functions and classes with no clear relationship.

**What is a flow?** Formally, a flow is defined as a DAG (Directed Acyclic Graph) with one source and one sink, meaning it has a beginning and an end. In practice, it is a sequence of steps that transform data from one form to another.

**Where can I use it?** Anywhere! Gloe is particularly useful for data science and machine learning pipelines, as well as for servers, scripts, or any area where there is a **gap between code and logical business understanding**.

**[Give me examples!](https://gloe.ideos.com.br/examples/index.html)**

## Key Features

- Write **type-safe** pipelines with pure Python.
- Express a pipeline as a set of **atomic**, **isolated**, **extensible** and **trackable** units of responsibility called [transformers](https://gloe.ideos.com.br/theory.html).
- [Validate the input, the output and the changes between them](https://gloe.ideos.com.br/getting-started/ensurers.html) of transformers during execution.
- [Mix sync and async](https://gloe.ideos.com.br/getting-started/async-transformers.html#async-pipelines) code without worrying about its concurrent nature.
- Keep your code **readable** and **maintainable**, even for **complex flows**. ¹ 
- Use it **anywhere** without changing your existing workflow.
- [Visualize you pipelines](https://gloe.ideos.com.br/getting-started/plotting.html) and the data flowing through them. ²
- Use a functional approach to work with [conditions](https://gloe.ideos.com.br/getting-started/conditional-flows.html) and [collections](https://gloe.ideos.com.br/api-reference/gloe.collection.html).

<sub>1. Gloe emerged in the context of a large application with extremely complex business logic. After transitioning the code to Gloe, maintenance efficiency improved by 200%, leading the entire team to adopt it widely.</sub>

<sub style="display: block; margin-top: -0.5rem;">2. This feature is under development.</sub>

## Installing

Requirements:
- Python (>= 3.9)
- typing-extensions (>= 4.7)

You can install Gloe using pip or conda:

```shell
# PyPI
pip install gloe
```

```shell
# or conda
conda install -c conda-forge gloe
```

## Example

Consider the following flow. It is part of an e-commerce server and starts from a HTTP request and ends with a list of recommended products. 


```python
get_recommendations = (
    extract_request_id >>
    get_user_by_id >> (
        get_last_seen_items,
        get_last_ordered_items,
        get_user_network_data,
    ) >>
    get_recommended_items
)
```

Steps of this flow:
1. The user ID is extracted from the request. 
2. The corresponding user data is retrieved using this ID. 
3. Three pieces of information about the user are gathered: the last seen items, the last ordered items, and the user's network data (such as personal information and relationships). 
4. These three pieces of information are used to generate a list of recommended items for this specific user.

Can we agree that it is easy to understand just by reading the code?

### Flow Steps: Transformers

Each step of a flow is called a **transformer** and creating one is as easy as:

```python
from gloe import transformer

@transformer
def extract_request_id(req: Request) -> int:
    # your logic goes here
```



You can connect many transformers using the right shift operator, just like the above example. When the argument of `>>` is a tuple, you are creating branches using the default [parallel gateway](). 

> Learn more about [creating transformers](https://gloe.ideos.com.br/getting-started/transformers.html), [pipelines](https://gloe.ideos.com.br/getting-started/transformers.html#building-a-pipeline), and [gateways](https://gloe.ideos.com.br/getting-started/gateways.html).

### Maintainance

When the manager requests you to return the items grouped by department instead of in a flat list, the refactoring process is straightforward:

```diff python
get_user_recommendations = (
    extract_request_id >>
    get_user_by_id >> (
        get_last_seen_items,
        get_last_ordered_items,
        get_user_network_data,
    ) >>
    get_recommended_items >>
    group_by_department
)
```

> See [full transformers definition](https://gloe.ideos.com.br/getting-started/plotting.html).

### Type checking

If, by some chance, you connect two transformers with incompatible types, the IDE along with [Mypy](https://github.com/python/mypy) will warn you about the malformed flow.

For example, suppose you implemented the `extract_request_id` transformer returning a string instead of a integer ID:

```python
@transformer
def extract_request_id(request: Request) -> str:
    ...
```

But the `get_user_by_id` transformer expects an `int` as input:

```python
@transformer
def get_user_by_id(user_id: int) -> User:
    ...
```

The result will be something like this:

![Malformed pipeline example](https://gloe.ideos.com.br/_images/malformed-pipeline-example.jpeg)

### Simple Usage

Considering is everything okay about the types, this pipeline can be invoked from a server, for example:

```python
@users_router.get('/:user_id/recommended')
def recommended_items_route(req: Request):
    return get_user_recommendations(req)
```

### Quick Documentation

When you need to document it somewhere, you can just [plot it](https://gloe.ideos.com.br/getting-started/plotting.html).

![Graph for send_promotion](https://gloe.ideos.com.br/_images/graph_example.jpeg)

### Integration 

Suppose you don't need to extract the user ID within the flow because you are using a web framework that already does it, like [FastAPI](https://fastapi.tiangolo.com/), you can remove the `extract_request_id` transformer. Since the incoming type for `get_user_by_id` is integer, the configuration would be:


```python
get_user_recommendations = (
    get_user_by_id >> (
        get_last_seen_items,
        get_last_ordered_items,
        get_user_network_data,
    ) >>
    get_recommended_items >>
    group_by_department
)


@users_router.get('/{user_id}/recommended')
def recommended_items_route(user_id: int):
    return get_user_recommendations(user_id)
```

We hope the above example illustrates how easily you can identify maintenance points and gain confidence that the rest of the code will continue to working properly, as long as the transformers' interfaces remain satisfied.


## Motivation

Software development has lots of patterns and good practices related to the code itself, like how to document, test, structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a successful software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artifacts and in a well-written code.

When developers write a code, they are telling a story to the next person who will read or/and refactor it. Depending on the code's quality, this story could be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software may take a long time to clearly understand the narrative and make it clear, or they will simply give up, leaving it as is.


### How Can Gloe Help Me?

Gloe comes to turn this story coherent, logically organized and easy to follow. This is achieved by dividing the code into [concise steps](https://gloe.ideos.com.br/theory.html) with an unambiguous responsibility and explicit interface. Then, Gloe allows you to connect these steps, clarifying their relationship and identifying necessary changes during refactoring. Thus, you can quickly understand the entire story being told and enhance it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implemented this approach using functional programming and strong typing concepts.

### Gloe is not a workflow orchestrator

Currently, unlike platforms like [Air Flow](https://airflow.apache.org/) that include scheduler backends for task orchestration, Gloe's primary purpose is to aid in development. The [graph structure](https://gloe.ideos.com.br/theory.html) aims to make the code [more flat and hence readable](https://en.wikibooks.org/wiki/Computer_Programming/Coding_Style/Minimize_nesting). However, it is important to note that Gloe does not offer functionalities for executing tasks in a dedicated environment, nor does it directly contribute to execution speed or scalability improvements.


## License

[Apache License Version 2.0](https://github.com/ideos/gloe/blob/main/LICENSE)