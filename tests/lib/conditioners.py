from gloe import condition


@condition
def if_not_zero(x: float) -> bool:
    return x != 0


@condition
def if_is_even(x: float) -> bool:
    return x % 2 == 0.0
