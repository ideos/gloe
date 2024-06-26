class NumberIsOdd(Exception):
    pass


class NumberIsEven(Exception):
    pass


class NumberLessThanOrEquals10(Exception):
    pass


class NumbersNotEqual(Exception):
    pass


class NumbersEqual(Exception):
    pass


class LnOfNegativeNumber(Exception):
    def __init__(self, num: float):
        super().__init__(
            f"The natural logarithm of the negative number {num} is not a real number"
        )


class HasNotBarKey(Exception):
    pass


class HasNotFooKey(Exception):
    pass


class HasFooKey(Exception):
    pass


class IsNotInt(Exception):
    pass
