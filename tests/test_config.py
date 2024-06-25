import re

import pytest
from unittest.mock import patch, mock_open
from main import get_config


@pytest.fixture()
def mock_toml_file():  # noqa: PT004
    toml_content = """
    [prompt.options]
    authors = ["Academic", "Professional"]
    audiences = ["General", "Technical"]
    essay_types = ["Argumentative", "Descriptive"]
    essay_tones = ["Formal", "Informal"]
    """
    with patch("builtins.open", mock_open(read_data=toml_content)):
        yield


def test_get_config_valid(mock_toml_file):  # noqa: ARG001
    config = get_config()
    assert config["author_options"] == ["Academic", "Professional"]
    assert config["audience_options"] == ["General", "Technical"]
    assert config["type_options"] == ["Argumentative", "Descriptive"]
    assert config["tone_options"] == ["Formal", "Informal"]


def test_get_config_missing_prompt_options():
    toml_content = """
    [other_section]
    key = "value"
    """
    with patch("builtins.open", mock_open(read_data=toml_content)), pytest.raises(
        ValueError,
        match=re.escape("[prompt.options] not found in essaybuddy.toml"),
    ):
        get_config()


def test_get_config_missing_authors():
    toml_content = """
    [prompt.options]
    audiences = ["General", "Technical"]
    essay_types = ["Argumentative", "Descriptive"]
    essay_tones = ["Formal", "Informal"]
    """
    with patch("builtins.open", mock_open(read_data=toml_content)), pytest.raises(
        ValueError,
        match="authors not found in essaybuddy.toml",
    ):
        get_config()


def test_get_config_missing_audiences():
    toml_content = """
    [prompt.options]
    authors = ["Academic", "Professional"]
    essay_types = ["Argumentative", "Descriptive"]
    essay_tones = ["Formal", "Informal"]
    """
    with patch("builtins.open", mock_open(read_data=toml_content)), pytest.raises(
        ValueError,
        match="audiences not found in essaybuddy.toml",
    ):
        get_config()


def test_get_config_missing_essay_types():
    toml_content = """
    [prompt.options]
    authors = ["Academic", "Professional"]
    audiences = ["General", "Technical"]
    essay_tones = ["Formal", "Informal"]
    """
    with patch("builtins.open", mock_open(read_data=toml_content)), pytest.raises(
        ValueError,
        match="essay_types not found in essaybuddy.toml",
    ):
        get_config()


def test_get_config_missing_essay_tones():
    toml_content = """
    [prompt.options]
    authors = ["Academic", "Professional"]
    audiences = ["General", "Technical"]
    essay_types = ["Argumentative", "Descriptive"]
    """
    with patch("builtins.open", mock_open(read_data=toml_content)), pytest.raises(
        ValueError,
        match="essay_tones not found in essaybuddy.toml",
    ):
        get_config()
