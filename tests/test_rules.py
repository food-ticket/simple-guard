import pytest

from simple_guard.rules import Pii, HarmfulContent, Topical


def test_rule_types():
    assert Pii().on == "input"
    assert Topical(["topic"]).on == "input"
    assert HarmfulContent().on == "output"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("My emailaddress is fake@simple-guard.com", False),
        ("Contact me on unknown@fakesite.com", False),
        ("Please contact me via email", True),
    ],
)
def test_pii_check_email(test_input, expected):
    rule = Pii()
    # Ignoring for testing purposes
    rule.on_fail = "ignore"
    assert rule.check(test_input).allowed == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("My name is Robert Downey Jr.", False),
        ("My friend Vanessa Hudgens", False),
        ("I'd like to keep my name secret", True),
    ],
)
def test_pii_check_person(test_input, expected):
    rule = Pii()
    # Ignoring for testing purposes
    rule.on_fail = "ignore"
    assert rule.check(test_input).allowed == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("My address is Rainbow Road 5 in Paris", False),
        ("I live on Sunshine Boulevard in Beverly Hills", False),
        ("My place of residence is not relevant in this case", True),
    ],
)
def test_pii_check_address(test_input, expected):
    rule = Pii()
    # Ignoring for testing purposes
    rule.on_fail = "ignore"
    assert rule.check(test_input).allowed == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("You can reach me at (555) 555-1234", False),
        ("Please call me on +(555) 122-1234", False),
        ("My phonenumber is known", True),
    ],
)
def test_pii_check_phone_number(test_input, expected):
    rule = Pii()
    # Ignoring for testing purposes
    rule.on_fail = "ignore"
    assert rule.check(test_input).allowed == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("My name is Robert Downey Jr.", "My name is <PERSON>"),
        ("My friend Vanessa Hudgens", "My friend <PERSON>"),
        ("I'd like to keep my name secret", "I'd like to keep my name secret"),
    ],
)
def test_pii_fix_person(test_input, expected):
    rule = Pii()
    rule.check(test_input)
    rule.fix()
    assert rule.content == expected
