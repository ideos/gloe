# High-Order Transformers

A common need you probably will have is to create transformers that receive other transformers as arguments. This is called high-order transformers. It is a powerful feature that allows you to create more complex transformers by combining simpler ones.

## Creating the "reduce" Transformer

Let's create a transformer that receives a list of integers and apply a "reducer" transformer to combine them sequentially. The types of this first example will be all static and the transformer will be called "reduce" (inspired by [`reduce`](https://realpython.com/python-reduce-function/)).

```python
from gloe import partial_transformer, transformer, Transformer

@partial_transformer
def reduce(
    data: list[int],
    reducer: Transformer[tuple[int, int], int],
    initial_value: int = 0
) -> int:
    result = initial_value
    for num in data:
        result = reducer((result, num))
    return result


@transformer
def sum_tuple2(data: tuple[int, int]) -> int:
    return data[0] + data[1]


sum_all = reduce(sum_tuple2)

print(sum_all([1, 2, 3, 4]))  # returns 10
```


## Creating the "Reduce" Generic Transformer

Now, let's create a more generic version of the "reduce" transformer. This time, we will use the `Generic` type from Python's `typing` module to allow the reducer to receive any type of data.

```python
from gloe import Transformer
from typing import Generic, TypeVar

T = TypeVar('T')
S = TypeVar('S')

class Reduce(Generic[T, S], Transformer[list[T], S]):
    def __init__(self, reducer: Transformer[tuple[S, T], S], initial_value: S):
        super().__init__()

        self.reducer = reducer
        self.initial_value = initial_value

    def transform(self, data: list[T]) -> S:
        result = self.initial_value
        for num in data:
            result = self.reducer((result, num))
        return result


flow = Reduce(sum_tuple2, initial_value=0.0)
print(sum_all([1, 2, 3, 4]))  # returns 10

``` 