import pytest
from main import validate_options


@pytest.fixture()
def config_options():
    return {
        "author_options": ["Author1", "Author2"],
        "audience_options": ["Audience1", "Audience2"],
        "type_options": ["Type1", "Type2"],
        "tone_options": ["Tone1", "Tone2"],
    }


def test_valid_options(config_options):
    essay_options = {
        "author": "Author1",
        "audience": "Audience1",
        "essay_type": "Type1",
        "tone": "Tone1",
    }
    assert validate_options(config_options, essay_options)


def test_invalid_author(config_options):
    essay_options = {
        "author": "InvalidAuthor",
        "audience": "Audience1",
        "essay_type": "Type1",
        "tone": "Tone1",
    }
    assert not validate_options(config_options, essay_options)


def test_invalid_audience(config_options):
    essay_options = {
        "author": "Author1",
        "audience": "InvalidAudience",
        "essay_type": "Type1",
        "tone": "Tone1",
    }
    assert not validate_options(config_options, essay_options)


def test_invalid_essay_type(config_options):
    essay_options = {
        "author": "Author1",
        "audience": "Audience1",
        "essay_type": "InvalidType",
        "tone": "Tone1",
    }
    assert (not validate_options(config_options, essay_options))


def test_invalid_tone(config_options):
    essay_options = {
        "author": "Author1",
        "audience": "Audience1",
        "essay_type": "Type1",
        "tone": "InvalidTone",
    }
    assert (not validate_options(config_options, essay_options))


def test_empty_options(config_options):
    essay_options = {"author": "", "audience": "", "essay_type": "", "tone": ""}
    assert (not validate_options(config_options, essay_options))


def test_missing_options(config_options):
    essay_options = {"author": "Author1", "audience": "Audience1"}
    with pytest.raises(KeyError):
        validate_options(config_options, essay_options)
