(creating-a-transformer)=
# Creating a Transformer

As previously said, creating a transformer is easy:

```python
from gloe import transformer

@transformer
def filter_even(numbers: list[int]) -> list[int]:
    """Filters out the even numbers from the input list."""
    return [num for num in numbers if num % 2 == 0]
```

Transformers work like functions, so you can create a function and then apply the `@transformer` decorator to it. That's it, transformer created!

```{admonition} Some important things to notice:
:class: important

- We **strongly recommend** you to type the transformers. Because of Python, it is not mandatory, but Gloe was designed to be used with typed code. Take a look at the [Python typing
library](https://docs.python.org/3/library/typing.html) to learn more about the Python type notation.
- Transformers must have only one parameter. Any complex data you need to use in its code must be passed in a complex structure like a [tuple](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences), a [dict](https://docs.python.org/3/tutorial/datastructures.html#dictionaries), a [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict), a [dataclass](https://docs.python.org/3/library/dataclasses.html), a [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) or any other. We will see later {ref}`why it is necessary <partial-transformers>`.
- Documentations with pydoc will be preserved in transformers.
- After applying the `@transformer` decorator to a function, it becomes an instance of the `Transformer` class.
```



Every transformer (instance of the Transformer class) can be called just like a normal function:

```python
filter_even([1, 2, 3, 4, 5, 6]) # returns [2, 4, 6]
```

Another way to create a transformer is extending from the Transformer class. This is how to implement the above example using a class instead of a function:

```python
from gloe import Transformer

class FilterEven(Transformer[list[int], list[int]]):
    """Filters out the even numbers from the input list."""
    
    def transform(self, numbers: list[int]) -> list[int]:
        return [num for num in numbers if num % 2 == 0]
```

However, in this case, we first need to instantiate the `FilterEven` class and then use the instance as a transformer:

```python
filter_even = FilterEven()

filter_even([1, 2, 3, 4, 5, 6]) # returns [2, 4, 6]
```

This doesn't seem useful when comparing to the first example, but maybe you would like to split your code into methods of a class in some cases. In fact, we try to avoid using classes to implement transformers to keep its code and responsibility clean and short.

## Building a Pipeline

You can create a pipeline by composing many transformers into a flow. You can do that by using the [right shift operator (>>)](https://docs.python.org/3/library/operator.html#operator.__rshift__). For example, consider the `filter_even` created above, we can create another transformer called `square`:

```python
@transformer
def square(numbers: list[int]) -> list[int]:
    return [num * num for num in numbers]
```

It is simple to compose these two transformers sequentially, it means, filter the even numbers and then square each of them:

```python
pipeline = filter_even >> square
```
```{admonition} Naming things
:class: seealso
We call this **serial connection**
```

By doing this, the `pipeline` variable becomes a transformer that executes the processing of the composed transformers sequentially. We can also call it as well:

```python
pipeline([1, 2, 3, 4, 5, 6]) # returns [4, 16, 36]
```

And you can continue appending transformers to the pipeline, even the ones already present there:

```python
pipeline = filter_even >> square >> square
```

You are also able to use this entire pipeline as a step of another flow:

```python
pipeline2 = pipeline >> my_transformer
```

### Creating branches

If you need to pass the data through two paths without a dependency between them, you can create branches.

Let's consider the example of a mailing system. We want to send a promotion email to users, but we have two types of users: the subscribed and the unsubscribed ones. We must retrieve the list of users from the database, split the groups and then send the appropriate email to each group:

```python
send_promotion = get_users >> (
    filter_subscribed >> send_subscribed_promotion_email,
    filter_unsubscribed >> send_unsubscribed_promotion_email
)
```
```{admonition} Naming things
:class: seealso
We call this **divergent connection**.
```


If it becomes necessary to treat each type of subscription, we can change the graph easily:

```python
send_promotion = get_users >> (
    filter_basic_subscription >> send_basic_subscription_promotion_email,
    filter_premium_subscription >> send_premium_subscription_promotion_email,
    filter_unsubscribed >> send_unsubscribed_promotion_email
)
```

This example makes it clear how easy it is to understand and refactor the code when using Gloe to express the process as a graph, with each node (transformer) having an atomic and well-defined responsibility.

```{important}
You should not assume any **order of execution** between branches.
```

The right shift operator can receive a transformer or a tuple of transformers as an argument. In the second case, the transformer returned will be as described bellow (pay attention to the types).

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

Of course, we can append a new transformer to the above graph, the only requirement is for the incoming type of this new transformer to be `tuple[Out1, Out2, ..., OutN]`.

```python
end: Transformer[tuple[Out1, Out2, ..., OutN], FinalOut]

graph: Transformer[In, FinalOut] = begin >> (
    branch1,
    branch2,
    ...,
    branchN
) >> end
```
```{admonition} Naming things
:class: seealso
We call this last connection **convergent**.
```

```{attention}
Python doesn't provide a generic way to map the outcome type of an arbitrary number of branches on a tuple of arbitrary size. Due to this, the overload of possible sizes was treated one by one until the size 7, it means, considering the typing notation, it is possible to have at most 7 branches currently.
```

