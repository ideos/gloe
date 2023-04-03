from src.gloe.conditional import conditioner


@conditioner
def if_not_zero(x: float) -> bool:
    return x != 0
