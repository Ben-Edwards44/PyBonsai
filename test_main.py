"""Tests for command-line option handling in main.py."""

import pytest

import main


def test_type_out_of_range_rejected():
    # --type documents "integer between 0 and 3 inclusive"; anything else
    # must be rejected instead of silently building a different tree.
    options = main.Options()
    with pytest.raises(Exception):
        options.set_option("--type", "5")


def test_type_non_integer_rejected():
    options = main.Options()
    with pytest.raises(Exception):
        options.set_option("--type", "abc")


def test_type_missing_value_rejected():
    # A bare `-t` flag carries no value (True); it must not silently
    # become tree type 1.
    options = main.Options()
    with pytest.raises(Exception):
        options.set_option("--type", True)


def test_type_valid_values_accepted():
    for value in ("0", "1", "2", "3"):
        options = main.Options()
        options.set_option("--type", value)
        assert options.type == int(value)
        assert options.user_set_type is True
