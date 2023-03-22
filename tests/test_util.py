import pytest

from util import head


@pytest.mark.parametrize(
    "test_input,expected", [([], None), (None, None), ([1], 1), ([1, 2], 1)]
)
def test_head(test_input, expected):
    assert head(test_input) == expected
