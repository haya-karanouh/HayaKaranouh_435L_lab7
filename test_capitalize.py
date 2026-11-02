import pytest

from capitalize import capital_case


def test_capital_case():
    assert capital_case("semaphore") == "Semaphore"


def test_raises_exception_on_non_string_arguments():
    with pytest.raises(TypeError, match="Please provide a string argument"):
        capital_case(9)


def test_accepts_string_subclass():
    class Text(str):
        pass

    assert capital_case(Text("haya")) == "Haya"
