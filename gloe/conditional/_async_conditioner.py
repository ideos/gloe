from typing_extensions import Self

from gloe.async_transformer import AsyncTransformer
from gloe.transformers import Transformer
from gloe.conditional._base_conditioner import BaseConditioner
from typing import TypeVar, Union, Optional, Callable

In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


class AsyncConditioner(
    BaseConditioner[In, ThenOut, ElseOut], AsyncTransformer[In, Union[ThenOut, ElseOut]]
):
    async def transform_async(self, data: In) -> Union[ThenOut, ElseOut]:
        for implication in self.implications:
            if implication.condition(data):
                if isinstance(implication.then_transformer, AsyncTransformer):
                    return await implication.then_transformer(data)
                elif isinstance(implication.then_transformer, Transformer):
                    return implication.then_transformer(data)

        if isinstance(self.else_transformer, AsyncTransformer):
            return await self.else_transformer(data)
        elif isinstance(self.else_transformer, Transformer):
            return self.else_transformer(data)

        raise NotImplementedError()

    def copy(
        self,
        transform: Optional[Callable[[Self, In], Union[ThenOut, ElseOut]]] = None,
        regenerate_instance_id: bool = False,
        force: bool = False,
    ) -> Self:
        return super().copy(transform, regenerate_instance_id, force)
