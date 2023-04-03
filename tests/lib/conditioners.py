from conditional import If, conditioner


@conditioner
def if_not_zero(x: float) -> bool:
    return x != 0
