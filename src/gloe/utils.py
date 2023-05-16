from typing import Any

from src.gloe.transformer import transformer


@transformer
def forget(data: Any) -> None:
    return None
