"""Capitalization exercise from Lab 7."""


def capital_case(x):
    if not isinstance(x, str):
        raise TypeError("Please provide a string argument")
    return x.capitalize()
