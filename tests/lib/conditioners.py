from gloe import conditioner


@conditioner
def if_not_zero(x: float) -> bool:
    return x != 0


@conditioner
def if_is_even(x: float) -> bool:
    return x % 2 == 0.0
