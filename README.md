***

<div align="center">
  <img src="./docs/assets/gloe-logo.png"><br>
</div>

Let Gloe help you
===

Gloe (pronounced /ɡloʊ/, like "glow") is a general purpose library made to help developers to create, maintain, document and test operational and data flows. It can be used in data science and machine learning pipelines as well in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not thought to be used in the entire application even less replacing any existing library, it was built to be integrated with other tools and to be implemented where the code complexity can be bigger than the desired.

## Table of Contents
<!-- TOC -->
  * [Motivation](#motivation)
  * [Installing](#installing)
  * [Gloe\'s theory](#gloes-theory)
    * [Lightness](#lightness)
    * [Type-safety](#type-safety)
    * [Immutability](#immutability)
    * [Non-linearity](#non-linearity)
  * [Getting Started](#getting-started)
    * [Creating a Transformer](#creating-a-transformer)
    * [Building a Pipeline](#building-a-pipeline)
      * [Creating branches](#creating-branches)
    * [Partial Transformers](#partial-transformers)
    * [Ensurers](#ensurers)
      * [A complete example](#a-complete-example)
    * [Conditioned Flows](#conditioned-flows)
    * [Utilities](#utilities)
      * [`forward`](#forward)
      * [`forward_incoming`](#forwardincoming)
      * [`side_effect`](#sideeffect)
      * [`debug`](#debug)
    * [Visualizing the graph (under development)](#visualizing-the-graph-under-development)
  * [Advanced Topics](#advanced-topics)
    * [Transformers with Generics](#transformers-with-generics)
    * [Creating your own utilities](#creating-your-own-utilities)
  * [Limitations](#limitations)
    * [Work in progress](#work-in-progress)
    * [Python limitations](#python-limitations)
<!-- TOC -->

## Motivation

The software development has a lot of patterns and good practices related to the code itself, like how to document, to test, to structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a well succeed software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artefacts and in a well-written code.

When a developer writes a code, he/she is telling a story to the next person who will read or/and refactor it. Depending on the quality of this code, this story could be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software will take a long time to understand the narrative and make it clear, or it will give up and leave it as it is.

Gloe comes to turn this story coherent, logically organized and easy to follow. This intends to be done dividing the code into concise steps with an unambiguous responsibility and explicit interface. Then, Gloe allow you to connect these steps, making clear how they can work together and where you need to make changes when doing some refactoring. Therefore, you will be able to quickly visualize all the story told and improve it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implemented this approach using functional programming and strong typing concepts.

## Installing

```shell
pip install gloe
```

## Gloe\'s theory

The main idea behind Gloe is constraint the implementation of a specific flow into a formalized and type-safe pipeline (or execution graph). Every piece (or node) of this pipeline is responsible to transform its input into the input of the next piece, composing a sequential execution process. No code of this flow can be executed out of these pieces and each node of a graph is called Transformer.

Basic structure of a Graph:
``` 
(type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> ... -> (type X)
```

> Type A is called **incoming type** and type X is called **outcome type** of
the graph.

A transformer must have an atomic and well-defined responsibility. As we will see later, implement a Transformer is a ridiculously easy task, so have many of them is not a problem. Keep it simple, make it easier to understand, document and test!

### Lightness

Gloe is a lightweight library, it is not a development environment nor an engine and nor even a heavy framework. It was built much more on top of **strong concepts** than an exhausting amount of code.

Its dependencies are only other python libraries, nothing external is required.

### Type-safety

Gloe was implemented to be completely type-safe. It means, when using Gloe, you must provide all the type hints of the created transformers, which can be summed up in its incoming and outcome types. Using these definitions, Gloe can warn about a malformed graph right away in the IDE and make precise inferring of extremely complex types.

For example, consider the bellow Transformer:

``` text
(type A) -> [MyTransformer] -> (type B)
```

The next transformer that can be appended to `MyTransformer`
must have the following signature:

``` text
(type B) -> [NextTransformer] -> (some type C)
```

That is, the outcome type of `MyTransformer` must be the same as the incoming type of `NextTransformer`. When building your graphs, you will know about any problem with types immediately.

> The representation of a transformer with its name and types is called
**signature**.

To perform this kind of behavior, Gloe uses the most recent and
sophisticated features of [Python typing
library](https://docs.python.org/3/library/typing.html).

### Immutability

An important concept adopted by Gloe is immutability. Every time a
Transformer is instantiated and appended as a next step of an existing
one, a new Transformer is created, merging the internal operations of
both transformers sequentially.

```
(type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> (type C)

Above graph is in fact this:

(type A) -> [Transformer 1 and 2] -> (type C)
```

It means every time we talked about a graph we are talking about a
Transformer too! A graph represents a Transformer that merge the
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

> To make easy our communication in this documentation, we will continue
to call the sequence of transformers as a **graph** and any range of
this sequence as a **subgraph**.

### Non-linearity

The term graph is motivated by the non-linearity characteristic of some
flows. A Transformer can pass its data to more than one posterior
transformers:

```
[Transformer 1]   -+->   [Transformer 2]   ->   [Transformer 3]   -+
                   |                                               |
                   +->   [Transformer 4]   ->   [Transformer 5]   -+->   [Transformer 6]
```

Any branch or ramification (transformers 2 and 3 or transformers 4 and 5 in above example) can have its own input and output types, and it can be of any length and including others ramifications.

## Getting Started

Now we have already learned the Gloe theory, so it's time to jump into code.   

### Creating a Transformer

As previously said, creating a transformer is easy:

```python
from gloe import transformer

@transformer
def filter_even(numbers: list[int]) -> list[int]:
    """Filters out the even numbers from the input list."""
    return [num for num in numbers if num % 2 == 0]
```

Transformers works like functions, so you can create a function and then apply the `@transformer` decorator to it. That's it, transformer created!

Some important things to notice:

- We **strongly recommend** you to type the transformers. Because of Python, it is not mandatory, but Gloe was designed to be used with typed code. Take a look at the [Python typing
library](https://docs.python.org/3/library/typing.html) to learn more about the Python type notation.
- Transformers must have only one parameter. Any complex data you need to use in its code must be passed in a complex structure like a [tuple](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences), a [dict](https://docs.python.org/3/tutorial/datastructures.html#dictionaries), a [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict), a [dataclass](https://docs.python.org/3/library/dataclasses.html), a [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) or any other. We will see later [why it is necessary](#partial-transformers).
- Documentations with pydoc will be preserved in transformers.
- After apply the `@transformer` decorator to a function, it will become an instance of class `Transformer`.

Every transformer (instance of the Transformer class) can be called just like a normal function:

```python
filter_even([1, 2, 3, 4, 5, 6]) # returns [2, 4, 6]
```

Another way to create a transformer is extending from the Transformer class. This is how implement the above example using a class instead of a function:

```python
from gloe import Transformer

class FilterEven(Transformer[list[int], list[int]]):
    """Filters out the even numbers from the input list."""
    
    def transform(self, numbers: list[int]) -> list[int]:
        return [num for num in numbers if num % 2 == 0]
```

However, in this case, we need first to instantiate the `FilterEven` class and then use the instance as a transformer:

```python
filter_even = FilterEven()

filter_even([1, 2, 3, 4, 5, 6]) # returns [2, 4, 6]
```

This doesn't seem useful when comparing to the first example, but maybe you would like to split your code into methods of a class in some cases. In fact, we try to avoid using classes to implement transformers to keep its code and responsibility clean and short.

### Building a Pipeline

The existence motivation of the transformers is composing many of them into an execution graph or pipeline. You can do that using the [right shift operator (>>)](https://docs.python.org/3/library/operator.html#operator.__rshift__). For example, consider the `filter_even` created above, we can create another transformer called `square`:

```python
@transformer
def square(numbers: list[int]) -> list[int]:
    return [num * num for num in numbers]
```

It is simple to compose these two transformers sequentially, it means, filter the even numbers and then square each of them:

```python
pipeline = filter_even >> square
```
> We call this **serial connection**

By doing that, the `pipeline` variable is also a transformer that execute sequentially the processing of the transformers used to build it. Of course, we can call it as well:

```python
pipeline([1, 2, 3, 4, 5, 6]) # returns [4, 16, 36]
```

And you can continue appending transformers to the pipeline, even the ones already present there:

```python
pipeline = filter_even >> square >> square
```

#### Creating branches

If you need to pass the data through two paths without a dependency between them, you can create branches.

Let's consider the example of a mailing system. We want to send a promotion email to users, but we have two types of users: the subscribed and the unsubscribed ones. We must retrieve the list of users from the database, split the groups and then send the appropriate email to each group:

```python
send_promotion = get_users >> (
    filter_subscribed >> send_subscribed_promotion_email,
    filter_unsubscribed >> send_unsubscribed_promotion_email
)
```
> We call this **divergent connection**.


If it becomes necessary to treat each type of subscription, we can change the graph easily:

```python
send_promotion = get_users >> (
    filter_basic_subscription >> send_basic_subscription_promotion_email,
    filter_premium_subscription >> send_premium_subscription_promotion_email,
    filter_unsubscribed >> send_unsubscribed_promotion_email
)
```
> This example makes clear how easy it is to understand and refactor the code when using Gloe to express the processing as a graph, with each node (transformer) having an atomic and well-defined responsibility.

> You can't assume any **order of execution** between the branches.

The right shift operator can receive a transformer or a tuple of transformers as an argument. In the second case, the transformer returned will be as described bellow (pay attention at the types).

Consider the following transformers:

```python
begin: Transformer[In, Mid]
branch1: Transformer[Mid, Out1]
branch2: Transformer[Mid, Out2]
...
branchN: Transformer[Mid, OutN]
```

Let's take a look at the type of the transformer returned by a divergent connection:
```python
graph: Transformer[In, tuple[Out1, Out2, ..., OutN]] = begin >> (
    branch1,
    branch2,
    ...,
    branchN
)
```

The return of each branch will compose a tuple following the respective order of branches.

Of course, we can append a new transformer to the above graph, the only requirement is the incoming type of this new transformer must be `tuple[Out1, Out2, ..., OutN]`.

```python
end: Transformer[tuple[Out1, Out2, ..., OutN], FinalOut]

graph: Transformer[In, FinalOut] = begin >> (
    branch1,
    branch2,
    ...,
    branchN
) >> end
```
> We call this last connection **convergent**.

> Python doesn't provide a generic way to map the outcome type of an arbitrary number of branches on a tuple of arbitrary size. Due to this, the overload of possible sizes was treated one by one until the size 7, it means, considering the typing notation, it is possible to have at most 7 branches currently.

### Partial Transformers

The single parameter of a transformer represents the input data during the execution and this input will be the return of the previous transformer in the pipeline. Given that, doesn't make sense allow transformers to have multiple parameters, because functions can't return multiple things (only a tuple of multiple things). However, sometimes we need some accessory data to perform the desired transformation.

For example, suppose we have a [Pandas](https://pandas.pydata.org/) dataframe of people with a numeric column "age". We want to filter people older than a specific age:

```python
@transformer
def filter_older_than_21(people_df: pd.DataFrame) -> pd.DataFrame:
    return people_df[people_df['age'] >= 21]
```

But maybe we would want to make this age threshold flexible. The first idea is to resort to the use of classes:

```python
class FilterOlderThan(Transformer[pd.DataFrame, pd.DataFrame]):
    def __init__(self, min_age: int):
        super().__init__() # don't forget that
        self.min_age = min_age

    def transform(self, people_df: pd.DataFrame) -> pd.DataFrame:
        return people_df[people_df['age'] >= self.min_age]
```

Now we can create many transformers with different ages:

```python
filter_older_than_21 = FilterOlderThan(min_age=21)
filter_older_than_18 = FilterOlderThan(min_age=18)
```

Gloe provide a much more easy way to implement this behavior using the `@partial_transformer` decorator. The same flexible transformer just created can be made using a functional approach:

```python
@partial_transformer
def filter_older_than(people_df: pd.DataFrame, min_age: int) -> pd.DataFrame:
    return people_df[people_df['age'] >= min_age]
```

It is possible to instantiate many transformers with different ages as well:

```python
filter_older_than_21 = filter_older_than(min_age=21)
filter_older_than_18 = filter_older_than(min_age=18)
```

In partial transformers, the first parameter is the input and all the remaining parameters are static and must be passed during the transformer instantiation. Another example:

```python
pipeline = filter_man >> filter_older_than(min_age=21)
```

> When typing the partial transformer instantiation, the IDE will ignore the first argument during autocompletion. 


### Ensurers

Although the type annotations are good enough to statically ensure a correct pipeline shape, on the other hand, there are some dynamic validations we may want to do on a transformer input and output during execution time. 

For example, consider the same `filter_even` transformer and suppose we only want positive numbers as its input. One first option is implement this logic inside the transformer code:

```python
@transformer
def filter_even(numbers: list[int]) -> list[int]:
    non_positives = [num for num in numbers if num % 2 == 0]
    if len(non_positives) > 0:
      raise Exception(f"The numbers {', '.join(non_positives)} are not positive.")
      
    return [num for num in numbers if num % 2 == 0]
```

In the above example, we are assigning a new responsibility to the transformer: the input validation. However, in many cases, we could have a complex validation or even many validations, and it seems a good idea to split the processing and these validations in different places. To help in this scenario, Gloe provides the `@ensure` decorator:

```python
def only_positive(numbers: list[int]):
  non_positives = [num for num in numbers if num % 2 == 0]
  if len(non_positives) > 0:
    raise Exception(f"The numbers {', '.join(non_positives)} are not positive.")


@ensure(incoming=[only_positive])
@transformer
def filter_even(numbers: list[int]) -> list[int]:
    return [num for num in numbers if num % 2 == 0]
```

In this version we are validating the incoming data outside the transformer, what allow us to refactor the validation step without change the transformer internal logic. 

The `@ensurer` decorator must be attached to a transformer and has the following parameters. All parameters receive a list of validators. A validator means just a normal function that perform a validation in the desired data and must throw an exception if the validation fails. The return of the validator is ignored.

- `incoming: list[Callable[[In], ...]]`: list of input validators. `In` type is the transformer incoming type.

- `outcome: list[Callable[[Out], ...]]`: list of output validators. `Out` type is the transformer outcome type.

- `changes: list[Callable[[In, Out], ...]]`: list of changes validators. A changes validator receives two parameters: the input and output data, which allow us to check if some kind of consistence is preserved after applying the transformation on the data. `In` and `Out` types are the transformer incoming type and outcome type, respectively.

#### A complete example

Suppose we have a Pandas dataframe of houses for sale, and we want to do an exploration of this data. This dataframe has many columns related to the houses' features (the city, for example) and a numeric column of "price". We want to find the cities with an average value of m² greater than a threshold (the implementations and pydocs will be omitted for simplicity):

```python
@partial_transformer
def cities_more_expensive_than(houses_df: pd.DataFrame, min_price: float) -> pd.DataFrame:
    ...
```

One input validation we want to do is ensure that there is not NaN values in the price column:

```python
def has_no_nan_prices(houses_df: pd.DataFrame):
    ...
```

A possible output validation is checking that exists at least one city that satisfies our condition:

```python
def is_non_empty(df: pd.DataFrame):
    ...
```

By last, maybe we would like to be sure that the lowest price in the selected cities is greater than the average value of all houses.

```python
def lowest_price_gt_avg(houses_df: pd.DataFrame, city_prices_df: pd.DataFrame):
    ...
```

Now we can add all these validations to our transformer:

```python
@ensure(incoming=[has_no_nan_prices], outcome=[is_non_empty], changes=[lowest_price_gt_avg])
@partial_transformer
def cities_more_expensive_than(houses_df: pd.DataFrame, min_price: float) -> pd.DataFrame:
    ...
```

> As you can see, the `@ensure` decorator works to partial transformers as well.

### Conditioned Flows

### Utilities

`forward`

`forward_incoming`

`side_effect`

`debug`


### Visualizing the graph (under development)

## Advanced Topics

### Transformers with Generics

If you need to use [generic types](https://mypy.readthedocs.io/en/stable/generics.html) in a transformer, this transformer must be partial. For example, suppose that, for some reason, you a need a transformer that swap the two elements of a tuple. If you don't care about the types within this tuple, you need generics:

```python
from typing import TypeVar
from gloe import partial_transformer

A = TypeVar("A")
B = TypeVar("B")

@partial_transformer
def swap_elements(pair: tuple[A, B]) -> tuple[B, A]:
  return pair[1], pair[0]
```
> When creating a partial transformer with only the input parameter, you must instantiate it with no arguments: `swap_elements()`.

> Of course, you can have a combination of generic types and multiple arguments, nothing changes.

In this case, the use of a partial transformer is required because Python can't infer the generic types from an instance of transformer when appending it to a graph, only from a function. Partial transformers are, in fact, builder functions that builds a transformer. So, when calling this function inside a graph, the transformer returned by the builder will already have the inferred types. For example:

```python
@transformer
def get_name_and_age(data: ...) -> tuple[str, int]: ...


graph = get_name_and_age >> swap_elements    # ❌ ERROR!

graph = get_name_and_age >> swap_elements()  # ✅ SUCCESS! 
```

The outcome type of the transformer `graph` in the success case is `tuple[int, str]`.


### Creating your own utilities

## Limitations

### Work in progress

The bellow limitations are already being investigated and will be released in the next versions.

- **Parallel execution**: branches in a graph are not executed in parallel nor concurrently yet.
- **Graph size limit**: Gloe was implemented using recursion to sequentially apply the transformations. Because of that, the graph size has a limit of nodes about 470, considering the default value of 1000 for the maximum depth of the Python interpreter stack. If you need an extremely large graph with thousands of nodes, you will need to [increase the recursion limit](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit) or wait us to release a recursion free version.

### Python limitations

The following limitations are inherited from Python and can be only solved when it is solved by the language or resorting to the use of third-party workarounds.

- **Overload transformers**: Python provide us a way to [overload function](https://docs.python.org/3/library/typing.html#typing.overload) definitions and [get its overloads](https://docs.python.org/3/library/typing.html#typing.get_overloads) at execution time. However, apparently, there is no way to forward all this overloads to a complex structure created from the overloaded function (like transformers). It is possible to be done considering only the execution but the type checker will not be aware of the overloads.

- **Higher-Kinded Types**: this is a feature of strong typed languages, like [Scala](https://www.baeldung.com/scala/higher-kinded-types), [Haskell](https://serokell.io/blog/kinds-and-hkts-in-haskell) and [Rust](https://hugopeters.me/posts/14/). However, even in Typescript there is an [open issue](https://github.com/microsoft/TypeScript/issues/1213) for that and in Java this must be [simulated](https://medium.com/@johnmcclean/simulating-higher-kinded-types-in-java-b52a18b72c74). So, it was to be expected that we can't use it natively in Python yet. But, there already is [a workaround](https://returns.readthedocs.io/en/latest/pages/hkt.html) for that from the [Returns](https://returns.readthedocs.io) library.