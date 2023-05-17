from typing import Any

from .transformer import transformer


@transformer
def forget(data: Any) -> None:
    return None
