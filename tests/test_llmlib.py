import pytest
from unittest.mock import MagicMock, patch
from llmlib import OpenAIConnection, request_completion


@pytest.fixture()
def mock_openai_connection():
    return OpenAIConnection("test_api_key", "test_endpoint_url")


@pytest.fixture()
def mock_messages():
    return [{"text": "Hello, how are you?"}]


def mock_completion():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "I'm fine, thank you."
    mock_completion.usage.total_tokens = 10
    mock_completion.usage.prompt_tokens = 5
    return mock_completion


def test_request_completion_correct_instance(mock_openai_connection, mock_messages):
    with patch("llmlib.OpenAI") as mock_openai, patch(
        "llmlib.sanitize_messages",
    ) as mock_sanitize_messages:
        mock_completion_response = mock_completion()
        mock_sanitize_messages.return_value = True
        mock_openai.return_value.chat.completions.create.return_value = (
            mock_completion_response
        )
        response = request_completion(mock_openai_connection, mock_messages)
        assert response == mock_completion_response.choices[0].message.content
        assert mock_openai.call_count == 1
        assert mock_sanitize_messages.call_count == 1


def test_request_completion_incorrect_instance(mock_messages):
    with pytest.raises(AssertionError) as e:
        request_completion("not_openai_connection", mock_messages)
    assert str(e.value) == "Expected oaiconn to be an instance of OpenAIConnection"


def test_request_completion_invalid_messages(mock_openai_connection):
    with pytest.raises(AssertionError) as e:
        request_completion(mock_openai_connection, ["not_a_dictionary"])
    assert str(e.value) == "All elements in messages must be dictionaries"


def test_request_completion_no_usage_info(mock_openai_connection):
    with patch("llmlib.OpenAI") as mock_openai:
        mock_completion.usage = None
        mock_openai.return_value.chat.completions.create.return_value = (
            mock_completion()
        )
        with pytest.raises(AssertionError):
            request_completion(mock_openai_connection, ["a", "b"])  # not a dict


def test_request_completion_no_message_in_completion(
    mock_openai_connection,
    mock_messages,
):
    with patch("llmlib.OpenAI") as mock_openai, patch(
        "llmlib.sanitize_messages",
    ) as mock_sanitize_messages:
        _mock_completion = mock_completion()
        mock_sanitize_messages.return_value = True
        _mock_completion.choices[0].message = None
        mock_openai.return_value.chat.completions.create.return_value = _mock_completion
        with pytest.raises(ValueError, match=r"No message in completion response"):
            request_completion(mock_openai_connection, mock_messages)


def test_request_completion_no_content_in_message(
    mock_openai_connection,
    mock_messages,
):
    with patch("llmlib.OpenAI") as mock_openai, patch(
        "llmlib.sanitize_messages",
    ) as mock_sanitize_messages:
        _mock_completion = mock_completion()
        mock_sanitize_messages.return_value = True
        _mock_completion.choices[0].message.content = None
        mock_openai.return_value.chat.completions.create.return_value = _mock_completion
        with pytest.raises(ValueError, match=r"No content in completion message"):
            request_completion(mock_openai_connection, mock_messages)
