***

<div align="center">
  <img src="./docs/assets/gloe-logo.png"><br>
</div>

# Let Gloe help you

Gloe (pronounced /ɡloʊ/, like "glow") is a general purpose library made to help developers to create, maintain, document and test operational and data flows. It can be used in data science and machine learning pipelines as well in servers, scripts or wherever else one identifies a lack between the code and the understanding of logical business. Gloe was not thought to be used in the entire application even less replacing any existing library, it was built to be integrated with other tools and to be implemented where the code complexity can be bigger than the desired.

## Table of Contents
<!-- TOC -->
* [Let Gloe help you](#let-gloe-help-you)
  * [Table of Contents](#table-of-contents)
  * [Installing](#installing)
  * [Gloe\'s paradigm](#gloes-paradigm)
    * [Lightness](#lightness)
    * [Type-safety](#type-safety)
    * [Immutability](#immutability)
    * [Non-linearity](#non-linearity)
  * [Getting Started](#getting-started)
    * [Creating a Transformer](#creating-a-transformer)
    * [Building a Pipeline](#building-a-pipeline)
    * [Partial Transformers](#partial-transformers)
    * [Ensurers](#ensurers)
<!-- TOC -->

## Installing

```shell
pip install gloe
```

## Gloe\'s paradigm

The main idea behind Gloe is constraint the implementation of a specific flow into a formalized and type-safe pipeline (or execution graph). Every piece (or node) of this pipeline is responsible to transform its input into the input of the next piece, composing a sequential execution process. No code of this flow can be executed out of these pieces. Each node of a graph is called Transformer.

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

That is, the outcome type of `MyTransformer` must be the same
as the incoming of `NextTransformer`. When building your
graphs, you will know about any problem with types immediately.

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

As previously said, creating a Transformer is easy:

```python
from gloe import transformer

@transformer
def filter_even(numbers: list[int]) -> list[int]:
    """Filters out the even numbers from the input list."""
    return [num for num in numbers if num % 2 == 0]
```

Transformer works like functions, so you can create a function and then apply the `@transformer` decorator to it. That's it, transformer created! Some important things to notice:

- We **strongly recommend** you to type the transformers. Because of Python, it is not mandatory, but Gloe was designed to be used with typed code. Take a look at the [Python typing
library](https://docs.python.org/3/library/typing.html) to learn more about the Python type notation.
- Transformers must have only one parameter. Any complex data you need to use in its code must be passed in a complex structure like a [tuple](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences), a [dict](https://docs.python.org/3/tutorial/datastructures.html#dictionaries), a [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict), a [dataclass](https://docs.python.org/3/library/dataclasses.html), a [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) or any other. We will see later why it is necessary.
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

However, in this case, we need first to instantiate the `FilterEvent` class and then use the instance as a transformer:

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

By doing that, the `pipeline` variable is also a transformer that execute sequentially the processing of the transformers used to build it. Of course, we can call it as well:

```python
pipeline([1, 2, 3, 4, 5, 6]) # returns [4, 16, 36]
```

And you can continue appending transformers to the pipeline, even the ones already present there:

```python
pipeline = filter_even >> square >> square
```

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