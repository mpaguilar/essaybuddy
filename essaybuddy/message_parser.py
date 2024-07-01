from nltk.tokenize import word_tokenize


def message_words(message: str) -> list[str]:
    """Tokenize a message into words."""

    # Tokenize the message into words
    words = word_tokenize(message)
    # Return the list of words
    return words
