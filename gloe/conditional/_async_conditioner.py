from typing_extensions import Self

from gloe.async_transformer import AsyncTransformer
from gloe.transformers import Transformer
from gloe.conditional._base_conditioner import BaseConditioner
from gloe.conditional._implication import _BaseImplication
from typing import TypeVar, Union, Sequence, Optional, Callable

In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


class AsyncConditioner(
    BaseConditioner[In, ThenOut, ElseOut], AsyncTransformer[In, Union[ThenOut, ElseOut]]
):
    def __init__(
        self,
        implications: Sequence[_BaseImplication[In, ThenOut]],
        else_transformer: AsyncTransformer[In, ElseOut],
    ):
        super().__init__(implications, else_transformer)
        self.else_transformer: AsyncTransformer[In, ElseOut] = else_transformer

    async def transform_async(self, data: In) -> Union[ThenOut, ElseOut]:
        for implication in self.implications:
            if implication.condition(data):
                if isinstance(implication.then_transformer, AsyncTransformer):
                    return await implication.then_transformer(data)
                elif isinstance(implication.then_transformer, Transformer):
                    return implication.then_transformer(data)

        return await self.else_transformer(data)

    def copy(
        self,
        transform: Optional[Callable[[Self, In], Union[ThenOut, ElseOut]]] = None,
        regenerate_instance_id: bool = False,
        force: bool = False,
    ) -> Self:
        return super().copy(transform, regenerate_instance_id, force)
