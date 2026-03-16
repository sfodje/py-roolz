import pytest

from roolz import get_operator, register_operator
from roolz.errors import UndefinedOperatorError
from datetime import datetime, timedelta, timezone as tz


def test_get_operator_undefined():
    with pytest.raises(UndefinedOperatorError):
        get_operator("undefined_operator")


def test_register_operator_already_registered():
    is_empty = get_operator("is_empty")
    with pytest.raises(ValueError):
        register_operator("is_empty", is_empty)


def test_operator_is_none():
    is_none = get_operator("is_none")
    assert is_none(None) is True
    assert is_none(0) is False


def test_operator_is_not_none():
    is_not_none = get_operator("is_not_none")
    assert is_not_none(None) is False
    assert is_not_none(0) is True


def test_operator_is_empty():
    is_empty = get_operator("is_empty")
    assert is_empty("") is True
    assert is_empty("not empty") is False
    assert is_empty([]) is True
    assert is_empty([1]) is False
    assert is_empty({}) is True
    assert is_empty({"key": "value"}) is False


def test_operator_is_not_empty():
    is_not_empty = get_operator("is_not_empty")
    assert is_not_empty("") is False
    assert is_not_empty("not empty") is True
    assert is_not_empty([]) is False
    assert is_not_empty([1]) is True
    assert is_not_empty({}) is False
    assert is_not_empty({"key": "value"}) is True


def test_operator_is_true():
    is_true = get_operator("is_true")
    assert is_true(True) is True
    assert is_true(False) is False
    assert is_true(0) is False
    assert is_true(1) is True
    assert is_true("") is False
    assert is_true("True") is True
    assert is_true("False") is False
    assert is_true(1.0) is True


def test_operator_is_false():
    is_false = get_operator("is_false")
    assert is_false(True) is False
    assert is_false(False) is True
    assert is_false(0) is True
    assert is_false(1) is False
    assert is_false("") is True
    assert is_false("True") is False
    assert is_false("False") is True


def test_operator_matches_regex():
    matches_regex = get_operator("matches_regex")
    assert matches_regex("abc", "^a.+") is True
    assert matches_regex("abc", "d") is False
    assert matches_regex("abc", "a.*") is True
    assert matches_regex("abc", "d.*") is False
    assert matches_regex("abc", "a.*c") is True
    assert matches_regex("abc", "d.*f") is False
    assert matches_regex("abc", "a.*c$") is True
    assert matches_regex("abc", "d.*f$") is False
    assert matches_regex("abc", "^a.*c$") is True
    assert matches_regex("abc", "^d.*f$") is False
    assert matches_regex("abc", ".*") is True
    assert matches_regex("abc", ".+") is True
    assert matches_regex("abc", ".") is False
    assert matches_regex("abc", "^$") is False
    assert matches_regex("abc", "$") is False
    assert matches_regex("abc", "^") is False
    assert matches_regex("abc", ".+c$") is True
    assert matches_regex("abc", "c") is False
    assert matches_regex("abc", "^c") is False
    assert matches_regex("abc", "^a..") is True
    assert matches_regex("abc", "a$") is False


def test_operator_date_between():
    now = datetime.now(tz=tz.utc)
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)
    date_between = get_operator("date_between")
    assert date_between(now, (past.isoformat(), future.isoformat())) is True
    assert date_between(now.isoformat(), (past, future)) is True
    assert date_between(now, (future.isoformat(), past.isoformat())) is False
    assert date_between(now, (future, past)) is False
    assert date_between('2021-01-01', ('2021-01-10', '2021-01-25')) is False
    assert date_between('2021-01-15', ('2021-01-10', '2021-01-25')) is True


def test_operator_one_of():
    one_of = get_operator("one_of")
    assert one_of("a", ["a", "b", "c"]) is True
    assert one_of("d", ["a", "b", "c"]) is False
    assert one_of(1, [1, 2, 3]) is True
    assert one_of(4, [1, 2, 3]) is False
    assert one_of(True, [True, False]) is True
    assert one_of(False, [True, False]) is True
    assert one_of("True", [True, False]) is False
    assert one_of("False", [True, False]) is False
    assert one_of(None, [None, 0, False]) is True
    assert one_of(0, [None, 0, False]) is True
    assert one_of(False, [None, 0, False]) is True
    assert one_of(1, [None, 0, False]) is False
    assert one_of(True, [None, 0, False]) is False
    assert one_of("None", [None, 0, False]) is False
    assert one_of("0", [None, 0, False]) is False
    assert one_of("False", [None, 0, False]) is False


def test_operator_less_than():
    less_than = get_operator("less_than")
    assert less_than(1, 2) is True
    assert less_than(2, 1) is False
    assert less_than(1, 1) is False
    assert less_than(1.0, 2) is True
    assert less_than(2, 1.0) is False
    assert less_than(1.0, 1.0) is False
    assert less_than(1, 2.0) is True
    assert less_than(2.0, 1) is False
    assert less_than(1.0, 2.0) is True
    assert less_than(2.0, 1.0) is False


def test_operator_greater_than():
    greater_than = get_operator("greater_than")
    assert greater_than(2, 1) is True
    assert greater_than(1, 2) is False
    assert greater_than(1, 1) is False
    assert greater_than(2, 1.0) is True
    assert greater_than(1.0, 2) is False
    assert greater_than(1.0, 1.0) is False
    assert greater_than(2.0, 1) is True
    assert greater_than(1, 2.0) is False
    assert greater_than(2.0, 1.0) is True
    assert greater_than(1.0, 2.0) is False


def test_operator_equal_to():
    equal_to = get_operator("equal_to")
    assert equal_to(1, 1) is True
    assert equal_to(1, 2) is False
    assert equal_to(1.0, 1) is True
    assert equal_to(1, 1.0) is True
    assert equal_to(1.0, 1.0) is True
    assert equal_to(1, 2.0) is False
    assert equal_to(2.0, 1) is False
    assert equal_to(1.0, 2.0) is False


def test_operator_not_equal_to():
    not_equal_to = get_operator("not_equal_to")
    assert not_equal_to(1, 1) is False
    assert not_equal_to(1, 2) is True
    assert not_equal_to(1.0, 1) is False
    assert not_equal_to(1, 1.0) is False
    assert not_equal_to(1.0, 1.0) is False
    assert not_equal_to(1, 2.0) is True
    assert not_equal_to(2.0, 1) is True
    assert not_equal_to(1.0, 2.0) is True


def test_operator_greater_than_or_equal_to():
    greater_than_or_equal_to = get_operator("greater_than_or_equal_to")
    assert greater_than_or_equal_to(2, 1) is True
    assert greater_than_or_equal_to(1, 2) is False
    assert greater_than_or_equal_to(1, 1) is True
    assert greater_than_or_equal_to(2, 1.0) is True
    assert greater_than_or_equal_to(1.0, 2) is False
    assert greater_than_or_equal_to(1.0, 1.0) is True
    assert greater_than_or_equal_to(2.0, 1) is True
    assert greater_than_or_equal_to(1, 2.0) is False
    assert greater_than_or_equal_to(2.0, 1.0) is True
    assert greater_than_or_equal_to(1.0, 2.0) is False


def test_operator_less_than_or_equal_to():
    less_than_or_equal_to = get_operator("less_than_or_equal_to")
    assert less_than_or_equal_to(1, 2) is True
    assert less_than_or_equal_to(2, 1) is False
    assert less_than_or_equal_to(1, 1) is True
    assert less_than_or_equal_to(1.0, 2) is True
    assert less_than_or_equal_to(2, 1.0) is False
    assert less_than_or_equal_to(1.0, 1.0) is True
    assert less_than_or_equal_to(1, 2.0) is True
    assert less_than_or_equal_to(2.0, 1) is False
    assert less_than_or_equal_to(1.0, 2.0) is True
    assert less_than_or_equal_to(2.0, 1.0) is False


def test_operator_starts_with():
    starts_with = get_operator("starts_with")
    assert starts_with("abc", "a") is True
    assert starts_with("abc", "b") is False
    assert starts_with("abc", "ab") is True
    assert starts_with("abc", "bc") is False
    assert starts_with("abc", "abc") is True
    assert starts_with("abc", "abcd") is False


def test_operator_ends_with():
    ends_with = get_operator("ends_with")
    assert ends_with("abc", "c") is True
    assert ends_with("abc", "b") is False
    assert ends_with("abc", "bc") is True
    assert ends_with("abc", "ab") is False
    assert ends_with("abc", "abc") is True
    assert ends_with("abc", "zabc") is False


def test_operator_contains():
    contains = get_operator("contains")
    assert contains("abc", "a") is True
    assert contains("abc", "b") is True
    assert contains("abc", "c") is True
    assert contains("abc", "d") is False
    assert contains("abc", "ab") is True
    assert contains("abc", "bc") is True
    assert contains("abc", "ac") is False
    assert contains("abc", "abc") is True
    assert contains("abc", "zabc") is False
    assert contains(["a", "b"], "b") is True


def test_operator_does_not_contain():
    does_not_contain = get_operator("does_not_contain")
    assert does_not_contain("abc", "a") is False
    assert does_not_contain("abc", "b") is False
    assert does_not_contain("abc", "c") is False
    assert does_not_contain("abc", "d") is True
    assert does_not_contain("abc", "ab") is False
    assert does_not_contain("abc", "bc") is False
    assert does_not_contain("abc", "ac") is True
    assert does_not_contain("abc", "abc") is False
    assert does_not_contain("abc", "zabc") is True
    assert does_not_contain(["a", "b"], "b") is False


def test_operator_contains_all():
    contains_all = get_operator("contains_all")
    assert contains_all("abc", ["a", "b", "c"]) is True
    assert contains_all("abc", ["a", "b", "d"]) is False
    assert contains_all("abc", ["a", "b"]) is True
    assert contains_all("abc", ["a", "d"]) is False
    assert contains_all("abc", ["a"]) is True
    assert contains_all("abc", ["d"]) is False
    assert contains_all("abc", []) is True
    assert contains_all("", ["a"]) is False
    assert contains_all("", []) is True
    assert contains_all([], ["a"]) is False
    assert contains_all([], []) is True
    assert contains_all(["a", "b", "c"], ["c", "b", "a"]) is True


def test_operator_contains_any():
    contains_any = get_operator("contains_any")
    assert contains_any("abc", ["a", "b", "c"]) is True
    assert contains_any("abc", ["a", "b", "d"]) is True
    assert contains_any("abc", ["a", "d"]) is True
    assert contains_any("abc", ["d", "e"]) is False
    assert contains_any("abc", ["d"]) is False
    assert contains_any("abc", []) is False
    assert contains_any("", ["a"]) is False
    assert contains_any("", []) is False
    assert contains_any([], ["a"]) is False
    assert contains_any([], []) is False
    assert contains_any(["a", "b", "c"], ["c", "b", "a"]) is True
    assert contains_any(["a", "b", "c"], ["d", "e", "f"]) is False


def test_operator_case_fold_equal_to():
    case_fold_equal_to = get_operator("case_fold_equal_to")
    assert case_fold_equal_to("abc", "abc") is True
    assert case_fold_equal_to("abc", "ABC") is True
    assert case_fold_equal_to("abc", "abC") is True
