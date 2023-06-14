import contextvars
import math
from contextvars import ContextVar
from typing import Tuple, Union

from networkx.drawing.nx_pydot import graphviz_layout
import networkx as nx
import matplotlib.pyplot as plt

from lib.transformers import minus1, to_string
from src.gloe import transformer
from src.gloe.conditional import conditioner
from src.gloe.mapper import Mapper
from tests.lib.transformers import square, square_root, sum1
from src.gloe.transformers import Begin, Transformer
from src.gloe.transformer_ensurer import ensure_with, input_ensurer

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
def format_output(strings: tuple[str, str]) -> (str, Transformer[int, float]):
    return ("\n".join(list(strings)), 1)


@conditioner
def if_not_zero(x: float) -> bool:
    return x != 0


# graph = sum1 >> square >> (
#     sum1 >> square >> if_not_zero.Then(
#         sum1 >> sum1 >> (
#             sum1 >> sum1,
#             sum1 >> sum1
#         )
#     ).Else(minus1 >> minus1) >> format_output,
#     sum1 >> square >> (
#         square >> Mapper([], square >> square_root) >> Begin() >>  square_root,
#         square >> square_root >> (
#             sum1 >> square,
#             sum1 >> square
#         )
#     ),
#     sum1 >> square >> (
#         sum1 >> square >> (
#             square >> square_root,
#             square >> square_root >> (
#                 sum1 >> square,
#                 sum1 >> square
#             )
#         )
#     )
# ) >> square >> square



@transformer
def is_even(x: float) -> bool:
    return x % 2 == 0

#
#
# else_if = (
#     is_even
#     .Then(square)
#     .ElseIf(lambda x: x < 2)
#     .Then(to_string)
#     .ElseNone()
# )
#
# conditional_graph = square >> (
#     is_even
#     .Then(square)
#     .ElseIf(lambda x: x < 2)
#     .Then(to_string)
#     .ElseNone()
# )
#
# reveal_type(ab)



if __name__ == '__main__':
    # graph.save('./process.svg')

    graph = logarithm(2)
    reveal_type(graph)

    # net = graph.export('net.dot', with_edge_labels=True)
    # pos = graphviz_layout(net, prog="dot")
    # nx.draw(net, pos)
    # plt.show()

# woman_process = filter_women >> filter_format
# print(woman_process(df), end='\n\n')
#
# man_process = filter_men >> filter_format
# print(man_process(df), end='\n\n')
# print(man_process)