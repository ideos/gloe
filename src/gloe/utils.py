from typing import Any

from .functional import transformer


@transformer
def forget(data: Any) -> None:
    return None
