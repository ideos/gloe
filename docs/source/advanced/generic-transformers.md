# Transformers With Generic Types

Currently, Gloe doesn't support the creation of transformers with generic types using the `@transformer` or any other decorator. However, you can still create transformers with generic types by using the `Transformer` class directly. Some examples are provided in the {py:mod}`gloe.collection` package.

## Creating the "Zip" Transformer

Suppose we want to build a transformer that receives two lists with the same length and we want to zip them. 

The input type of the transformer is a tuple with two lists of the different types: list1 with type `list[T]` and list2 with type `list[S]`. So, the input type of the Zip transformer is `tuple[list[T], list[U]]`

The output type is a list of tuples, each tuple with type `tuple[T, S]`. So, the output type of the Zip transformer is `list[tuple[T, S]]`.

Lets implement the Zip transformer using the `Transformer` class directly:

```python
from typing import TypeVar, Generic
from gloe import Transformer

T = TypeVar("T")
U = TypeVar("U")

class Zip(Generic[T, U], Transformer[tuple[list[T], list[U]], list[tuple[T, U]]]):
    def transform(self, data: tuple[list[T], list[U]]) -> list[tuple[T, U]]:
        list1, list2 = data
        return list(zip(list1, list2))
```

```{note}
For more information about the `Transformer` class, check {class}`gloe.Transformer`.
```

With this class, we can use each in different types of lists:

```python
list1 = [1, 2, 3]
list2 = ["a", "b", "c"]

zip_transformer = Zip[int, str]()

output = zip_transformer(list1, list2)
print(output)  # [(1, 'a'), (2, 'b'), (3, 'c')]
```