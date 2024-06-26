from gloe.conditional._base_conditioner import BaseConditioner
from gloe.conditional._implication import _Implication
from typing import (
    TypeVar,
    Union,
    Sequence,
)

from gloe.transformers import Transformer


In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


class Conditioner(
    BaseConditioner[In, ThenOut, ElseOut], Transformer[In, Union[ThenOut, ElseOut]]
):
    def __init__(
        self,
        implications: Sequence[_Implication[In, ThenOut]],
        else_transformer: Transformer[In, ElseOut],
    ):
        super().__init__(implications, else_transformer)
        self.implications: Sequence[_Implication[In, ThenOut]] = implications
        self.else_transformer: Transformer[In, ElseOut] = else_transformer

    def transform(self, data: In) -> Union[ThenOut, ElseOut]:
        for implication in self.implications:
            if implication.condition(data):
                return implication.then_transformer(data)

        return self.else_transformer(data)
