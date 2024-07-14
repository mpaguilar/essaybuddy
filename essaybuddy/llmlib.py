import logging
from dataclasses import dataclass
from string import Template

from message_parser import message_words
from openai import OpenAI
from openai.types.chat import ChatCompletion
from prompts import completion_check

log = logging.getLogger(__name__)


@dataclass
class OpenAIConnection:
    """Hold credentials and stats for an OAI-compaitible endpoint."""

    api_key: str
    endpoint_url: str
    request_tokens: int = 0
    response_tokens: int = 0

    def update_stats(self, chat_completion: ChatCompletion) -> None:
        """Update request and response token counts."""

        self.request_tokens += chat_completion.usage.prompt_tokens
        self.response_tokens += chat_completion.usage.completion_tokens


def request_completion(
    oaiconn: OpenAIConnection,
    messages: list,
    model: str = "gpt-4o",
) -> str:
    """Request a completion from the OpenAI API.

    Parameters
    ----------
    oaiconn : OpenAIConnection
        An instance of the OpenAIConnection class.
    messages : list of dict
        A list of dictionaries representing the messages to send to the API.
    model : str, optional
        The name of the model to use for the completion. Default is 'gpt-4o'.

    Returns
    -------
    str
        The content of the completion message.

    Raises
    ------
    AssertionError
        If `oaiconn` is not an instance of OpenAIConnection, or if any element
        in `messages` is not a dictionary.
    ValueError
        If `messages` fails sanitization, if there is no usage information in
        the completion response, if there is no message in the completion
        response, or if there is no content in the completion message.

    Notes
    -----
    This function performs the following steps:

    1. Asserts that `oaiconn` is an instance of OpenAIConnection and that all
       elements in `messages` are dictionaries.
    2. Sanitizes the messages.
    3. Creates an OpenAI client using the API key and endpoint URL from
       `oaiconn`.
    4. Calls the OpenAI API to create a completion using the specified model
       and messages.
    5. Updates the stats of `oaiconn` using the completion response.
    6. Extracts the content of the completion message from the completion
       response.

    """

    assert isinstance(
        oaiconn,
        OpenAIConnection,
    ), "Expected oaiconn to be an instance of OpenAIConnection"

    assert all(
        isinstance(message, dict) for message in messages
    ), "All elements in messages must be dictionaries"

    if not sanitize_messages(messages):
        _msg = "Messages failed sanitization"
        log.error(_msg)
        raise ValueError(_msg)

    _client = OpenAI(
        api_key=oaiconn.api_key,
        base_url=oaiconn.endpoint_url,
    )

    _completion = _client.chat.completions.create(
        model=model,
        messages=messages,
    )

    oaiconn.update_stats(_completion)

    _msg = f"Received reply of {len(str(_completion.choices[0].message))} length."

    _usage = _completion.usage
    if _usage is None:
        _msg = "No usage information in completion response"
        log.error(_msg)
        raise ValueError(_msg)

    _completion_message = _completion.choices[0].message

    if _completion_message is None:
        _msg = "No message in completion response"
        log.error(_msg)
        raise ValueError(_msg)

    if _completion_message.content is None:
        _msg = "No content in completion message"
        log.error(_msg)
        raise ValueError(_msg)

    return _completion_message.content


def sanitize_messages(messages: list) -> bool:
    """Sanitize messages for prompt injections.

    This app is pretty easy since there will be only two messages: the system
    message and the user message. We only need to check the user message.

    """

    # Check if the list has at least two elements
    if len(messages) < 2:  # noqa: PLR2004
        _msg = "The list must have at least two elements"
        log.error(_msg)
        raise ValueError(_msg)

    # Check if the second element is a dictionary
    if not isinstance(messages[1], dict):
        _msg = "The second element must be a dictionary"
        log.error(_msg)
        raise TypeError(_msg)

    # Check if the dictionary has a 'content' key
    if "content" not in messages[1]:
        _msg = "The dictionary must have a 'content' key"
        log.error(_msg)
        raise ValueError(_msg)

    # Check if the 'content' value is a string
    if not isinstance(messages[1]["content"], str):
        _msg = "The 'content' value must be a string"
        log.error(_msg)
        raise TypeError(_msg)

    return True


def check_completion(
    oaiconn: OpenAIConnection,
    completion_text: str,
    model: str = "gpt-4o",
) -> bool:
    """Check if the completion text is valid."""

    _system_msg = completion_check.system_msg
    _prompt_msg = Template(completion_check.prompt_msg).substitute(
        response=completion_text,
    )

    _messages = [
        {
            "role": "system",
            "content": _system_msg,
        },
        {
            "role": "user",
            "content": _prompt_msg,
        },
    ]

    _client = OpenAI(
        api_key=oaiconn.api_key,
        base_url=oaiconn.endpoint_url,
    )

    _completion = _client.chat.completions.create(
        model=model,
        messages=_messages,
    )

    _msg = f"Received reply of {len(str(_completion.choices[0].message))} length."

    _usage = _completion.usage
    if _usage is None:
        _msg = "No usage information in completion response"
        log.error(_msg)
        raise ValueError(_msg)

    oaiconn.update_stats(_completion)

    _completion_message = _completion.choices[0].message

    if _completion_message is None:
        _msg = "No message in completion response"
        log.error(_msg)
        raise ValueError(_msg)

    if _completion_message.content is None:
        _msg = "No content in completion message"
        log.error(_msg)
        raise ValueError(_msg)

    _first_word = message_words(_completion_message.content)[0].lower()

    if _first_word == "accepted":
        return True

    if _first_word == "rejected":
        _msg = "Completion check rejected."
        log.error(_msg)
        _msg = f"Completion check rejected: {_completion_message.content}"
        log.error(_msg)
        return False

    _msg = f"Invalid response from completion check: {_completion_message.content}"
    log.error(_msg)
    raise ValueError(_msg)
