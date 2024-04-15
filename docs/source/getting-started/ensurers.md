(ensurers)=
# Ensurers

```{admonition} API Reference
:class: seealso
- {func}`gloe.ensure`
```

Although the type annotations are good enough to statically ensure a correct pipeline shape, on the other hand, there are some dynamic validations we may want to do on a transformer input and output during execution time. 

For example, consider the same `filter_even` transformer and suppose we only want positive numbers as its input. One first option is implement this logic inside the transformer code:

```python
@transformer
def filter_even(numbers: list[int]) -> list[int]:
    non_positives = [num for num in numbers if num <= 0]
    if len(non_positives) > 0:
      raise Exception(f"The numbers {', '.join(non_positives)} are not positive.")
      
    return [num for num in numbers if num % 2 == 0]
```

In the example above, we are assigning a new responsibility to the transformer: the input validation. However, in many cases, we could have many complex validations, and it may be a good idea to keep processes and validations in different places. To help in this scenario, Gloe provides the `@ensure` decorator:

```python
def only_positive(numbers: list[int]):
  non_positives = [num for num in numbers if num <= 0]
  if len(non_positives) > 0:
    raise Exception(f"The numbers {', '.join(non_positives)} are not positive.")


@ensure(incoming=[only_positive])
@transformer
def filter_even(numbers: list[int]) -> list[int]:
    return [num for num in numbers if num % 2 == 0]
```

In this version we are validating the incoming data outside the transformer, which allows us to refactor the validation step without changing the transformer internal logic. 

The `@ensure` decorator must be attached to a transformer and have the following parameters. All parameters receive a list of validators. A validator is a function that performs a validation in the desired data and must throw an exception if the validation fails. The return of the validator is ignored.

- `incoming: list[Callable[[In], ...]]`: list of input validators. `In` type is the transformer incoming type.

- `outcome: list[Callable[[Out], ...]]`: list of output validators. `Out` type is the transformer outcome type.

- `changes: list[Callable[[In, Out], ...]]`: list of changes validators. A changes validator receives two parameters: the input and output data, which allow us to check if some kind of consistence is preserved after applying the transformation on the data. `In` and `Out` types are the transformer incoming type and outcome type, respectively.

## A complete example

Suppose we have a Pandas dataframe of houses for sale, and we want to explore this data. This dataframe may have many columns related to the houses' features (the city, for example) and a numeric column of "price", for example. We want to find the cities with an average value of m² greater than a threshold (the implementations and pydocs will be omitted for simplicity):

```python
@partial_transformer
def cities_more_expensive_than(houses_df: pd.DataFrame, min_price: float) -> pd.DataFrame:
    ...
```

One input validation we may want to do is ensure that there is not NaN values in the price column:

```python
def has_no_nan_prices(houses_df: pd.DataFrame):
    ...
```

Another possible output validation is checking that exists at least one city that satisfies our condition:

```python
def is_non_empty(df: pd.DataFrame):
    ...
```

Lastly, maybe we would like to be sure that the lowest price in the selected cities is greater than the average value of all houses.

```python
def lowest_price_gt_avg(houses_df: pd.DataFrame, city_prices_df: pd.DataFrame):
    ...
```

Now we can add all these validations to our transformer:

```python
@ensure(
    incoming=[has_no_nan_prices],
    outcome=[is_non_empty],
    changes=[lowest_price_gt_avg]
)
@partial_transformer
def cities_more_expensive_than(houses_df: pd.DataFrame, min_price: float) -> pd.DataFrame:
    ...
```
```{important}
As you can see, the `@ensure` decorator works with partial transformers as well. In fact, you can use it with all types of transformers, including async transformers and partial async transformers.
```
