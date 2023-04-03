import typing
from typing import List, ParamSpec, Tuple, TypeVar
from typing_extensions import TypeVarTuple, Unpack

from conditional import If, conditioner
from tests.lib.transformers import square, square_root, sum1
from transformer import Begin, Blank, transformer
from transformer_ensurer import ensure_with, input_ensurer

import pandas as pd

df = pd.DataFrame(
    {
        "name": ["John", "Mary", "Anne"],
        "age": [10, 17, 20],
        "sex": ["male", "female", "female"],
    }
)


@transformer
def filter_women(people_df: pd.DataFrame) -> pd.DataFrame:
    return people_df.loc[people_df['sex'] == 'female']


@transformer
def filter_men(people_df: pd.DataFrame) -> pd.DataFrame:
    return people_df.loc[people_df['sex'] == 'male']


@transformer
def filter_adult(people_df: pd.DataFrame) -> pd.DataFrame:
    return people_df.loc[people_df['age'] >= 18]


graph_func = lambda df: filter_women(filter_men(filter_adult(df)))


@transformer
def filter_minor(people_df: pd.DataFrame) -> pd.DataFrame:
    return people_df.loc[people_df['age'] < 18]


@input_ensurer
def ensure_schema(people_df: pd.DataFrame):
    required_cols = {'name', 'age', 'sex', 'birthday'}
    if not required_cols.issubset(people_df.columns):
        formatted_missing_cols = ", ".join(required_cols.difference(people_df.columns))
        raise Exception(f'Missing columns: {formatted_missing_cols}')


@ensure_with([ensure_schema])
@transformer
def format_introduction(people_df: pd.DataFrame) -> str:
    return "\n".join(
        [
            f"Hi! My name is {row['name']} and I'm {row['age']} years old."
            for _, row in people_df.iterrows()
        ]
    )


@transformer
def format_output(strings: tuple[str, str]) -> str:
    return "\n".join(list(strings))


@conditioner
def if_not_zero(x: float) -> bool:
    return x != 0


graph = sum1 >> square >> (
    square_root >> sum1 >> square,
    square_root >> square >> square_root >> square >> square_root >> (
        square >> square_root,
        square >> square_root,
    ),
    square_root >> square >> square_root
)

filter_1 = filter_women >> filter_minor
filter_2 = filter_adult >> format_introduction

graph2 = filter_1 >> filter_1 >> if_not_zero.Then(filter_1).Else(filter_2)

if __name__ == '__main__':
    print(graph(1))
    # graph.save('./process.svg')

# woman_process = filter_women >> filter_format
# print(woman_process(df), end='\n\n')
#
# man_process = filter_men >> filter_format
# print(man_process(df), end='\n\n')
# print(man_process)
