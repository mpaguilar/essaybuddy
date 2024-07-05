import logging
import os

import streamlit as st
import tomlkit
from essaylib import Essay, EssayOptions, run_request

logging.basicConfig(level=logging.DEBUG)

# Set these to WARNING to reduce noise in the logs
_set_to_warning_level = [
    "httpcore",
    "httpx",
    "urllib3",
    "openai",
    "watchdog",
]

for _logger_name in _set_to_warning_level:
    logging.getLogger(_logger_name).setLevel(logging.WARNING)

log = logging.getLogger(__name__)

open_ai_key = os.getenv("OPENAI_API_KEY")
if open_ai_key is None:
    _msg = "OPENAI_API_KEY environment variable not set"
    log.error(_msg)
    raise ValueError(_msg)


def get_config(config_file: str = "essaybuddy.toml") -> dict:
    """Load and validate the configuration from a TOML file.

    Parameters
    ----------
    config_file : str, optional
        The path to the TOML configuration file. Default is "essaybuddy.toml".

    Returns
    -------
    dict
        A dictionary containing the validated configuration options.

    Raises
    ------
    ValueError
        If the required configuration options are not found in the TOML file.

    Notes
    -----
    This function performs the following steps:
    1. Load the configuration from the specified TOML file.
    2. Check if the "prompt_options" section exists in the configuration.
    3. Validate and extract the "authors", "audiences", "essay_types", and "essay_tones"
    4. Return a dictionary containing the validated configuration options.

    """
    with open(config_file) as _toml:
        _config = tomlkit.load(_toml)

    if not _config.get("prompt", {}).get("options"):
        _msg = f"[prompt.options] not found in {config_file}"
        log.error(_msg)
        raise ValueError(_msg)

    _prompt_options = _config["prompt"]["options"]

    # "I am a..."
    if not _prompt_options.get("authors"):
        _msg = f"authors not found in {config_file}"
        log.error(_msg)
        raise ValueError(_msg)

    _author_options = _prompt_options["authors"]

    # "I am writing for..."
    if not _prompt_options.get("audiences"):
        _msg = f"audiences not found in {config_file}"
        log.error(_msg)
        raise ValueError(_msg)

    _audience_options = _prompt_options["audiences"]

    # "I am writing..."
    if not _prompt_options.get("essay_types"):
        _msg = f"essay_types not found in {config_file}"
        log.error(_msg)
        raise ValueError(_msg)

    _type_options = _prompt_options["essay_types"]

    # "The tone should be..."
    if not _prompt_options.get("essay_tones"):
        _msg = f"essay_tones not found in {config_file}"
        log.error(_msg)
        raise ValueError(_msg)

    _tone_options = _prompt_options["essay_tones"]

    return {
        "author_options": _author_options,
        "audience_options": _audience_options,
        "type_options": _type_options,
        "tone_options": _tone_options,
    }


def validate_options(config_options: dict, essay_options: EssayOptions) -> bool:
    """Validate the essay options.

    The reason for the dropdowns is to limit opportunities for injection.
    This won't work very well if they bypass the dropdown via curl, or something.
    1. Check that the author is in the list of valid authors.
    2. Check that the audience is in the list of valid audiences.
    3. Check that the essay type is in the list of valid essay types.
    4. Check that the tone is in the list of valid tones.

    """

    # Check that the author is in the list of valid authors.
    if essay_options["author"] not in config_options["author_options"]:
        return False

    # Check that the audience is in the list of valid audiences.
    if essay_options["audience"] not in config_options["audience_options"]:
        return False

    # Check that the essay type is in the list of valid essay types.
    if essay_options["essay_type"] not in config_options["type_options"]:
        return False

    # Check that the tone is in the list of valid tones.
    if essay_options["tone"] not in config_options["tone_options"]:  # noqa: SIM103
        return False

    return True


def st_go() -> None:
    """Run the main Streamlit app."""

    _config: dict = get_config()
    assert isinstance(_config, dict), "_config should be a dictionary"

    _essay = Essay()
    _essay_txt = _essay.load()

    # Set the page title and icon
    st.set_page_config(page_title="Essay Buddy", page_icon=":pencil2:", layout="wide")

    _content = "### Results will show here after you submit the essay."

    col1, col2 = st.columns(2)
    _submitted = False

    with col1, st.form("essay_form"):
        # build the selection boxes
        _author = st.selectbox("I am a...", _config["author_options"])
        _audience = st.selectbox("I am writing for...", _config["audience_options"])
        _essay_type = st.selectbox("I am writing...", _config["type_options"])
        _tone = st.selectbox("The tone should be...", _config["tone_options"])
        _essay_txt = st.text_area("Essay", value=_essay_txt, height=800)

        # Add a couple of buttons
        _button_col1, button_col2 = st.columns(2)
        with _button_col1:
            _submitted = st.form_submit_button("Submit")
        with button_col2:
            _save = st.form_submit_button("Save")

        _essay_options = EssayOptions(
            {
                "author": _author,
                "audience": _audience,
                "essay_type": _essay_type,
                "tone": _tone,
            },
        )

    with col2:
        if _submitted:
            if not validate_options(_config, _essay_options):
                st.error("Invalid options.")
                return

            with st.spinner("Working on it..."):

                _content = run_request(
                    _essay_txt,
                    essay_options=_essay_options,
                    open_ai_key=open_ai_key,
                    model="gpt-4o",
                )

                _essay.save(_essay_txt)

        if _save:
            _essay.save(_essay_txt)

        st.write(_content)


if __name__ == "__main__":
    st_go()
