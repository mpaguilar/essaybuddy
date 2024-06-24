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
