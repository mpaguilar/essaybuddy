import logging
from dataclasses import dataclass

from openai import OpenAI

log = logging.getLogger(__name__)


@dataclass
class OpenAIConnection:
    """Hold credentials and stats for an OAI-compaitible endpoint."""

    api_key: str
    endpoint_url: str = "https://api.openai.com/v1/"
    request_tokens: int = 0
    response_tokens: int = 0


def request_completion(
    oaiconn: OpenAIConnection,
    messages: list,
    model: str = "gpt-4o",
) -> str:
    """Request completion from OpenAI API.

    Parameters
    ----------
    oaiconn : OpenAIConnection
        Instance to manage tokens for request and response.

    messages : list
        A list of dictionaries representing conversation messages.

    model : str, optional
        The model to use for completion, by default "gpt-40".

    Returns
    -------
    str
        Content of the first choice in reply from OpenAI API as a string.

    Raises
    ------
    AssertionError
        If `oaiconn` is not an instance of OpenAIConnection
        or if any list element in `messages` does not have 'text' key with str value.

    """

    assert isinstance(
        oaiconn,
        OpenAIConnection,
    ), "Expected oaiconn to be an instance of OpenAIConnection"

    assert all(
        isinstance(message, dict) for message in messages
    ), "All elements in messages must be dictionaries"

    sanitize_messages(messages)

    _client = OpenAI(
        api_key=oaiconn.api_key,
        base_url=oaiconn.endpoint_url,
    )

    _completion = _client.chat.completions.create(
        model=model,
        messages=messages,
    )

    _msg = f"Received reply of {len(str(_completion.choices[0].message))} length."

    _usage = _completion.usage
    if _usage is None:
        _msg = "No usage information in completion response"
        log.error(_msg)
        raise ValueError(_msg)

    _reply_tokens = _usage.total_tokens - _usage.prompt_tokens
    oaiconn.request_tokens += _usage.prompt_tokens
    oaiconn.response_tokens += _reply_tokens

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


def sanitize_messages(messages: list) -> list:
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

    return messages
