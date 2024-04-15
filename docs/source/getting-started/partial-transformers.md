(partial-transformers)=
# Partial Transformers


```{admonition} API Reference
:class: seealso
- {func}`gloe.partial_transformer`
```

The single parameter of a transformer represents the input data during the execution and this input will be the return of the previous transformer in the pipeline. That being said, it doesn't make sense to allow transformers to have multiple parameters, because functions can't return multiple things (only a tuple of multiple things). However, sometimes we need some accessory data to perform the desired transformation.

For example, suppose we have a [Pandas](https://pandas.pydata.org/) dataframe of people with a numeric column "age". We want to filter people older than a specific age:

```python
@transformer
def filter_older_than_21(people_df: pd.DataFrame) -> pd.DataFrame:
    return people_df[people_df['age'] >= 21]
```

But maybe we want to make this age threshold flexible. The first idea is to resort to the use of classes:

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

Gloe provides a much easier way to implement this behavior using the `@partial_transformer` decorator. We can then create the same transformer using a functional approach:

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
```{tip}
When typing the partial transformer instantiation, IDEs will ignore the first argument during autocompletion.
```
