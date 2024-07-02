from message_parser import message_words


def test_message_words():
    # Check if the function correctly tokenizes a simple message
    assert message_words("Hello, world!") == ["Hello", ",", "world", "!"]

    # Check if the function correctly tokenizes a message with punctuation
    assert message_words("It's a beautiful day.") == [
        "It",
        "'s",
        "a",
        "beautiful",
        "day",
        ".",
    ]

    # Check if the function correctly handles an empty message
    assert message_words("") == []

    # Check if the function correctly handles a message with only punctuation
    assert message_words("!!!") == ["!", "!", "!"]

    # Check if the function correctly handles a message with numbers
    assert message_words("I have 2 apples and 3 oranges.") == [
        "I",
        "have",
        "2",
        "apples",
        "and",
        "3",
        "oranges",
        ".",
    ]

    # Check if the function correctly handles a message with special characters
    assert message_words("Hello, @world!") == ["Hello", ",", "@", "world", "!"]

    # Check if the function correctly handles a message with multiple spaces
    assert message_words("Hello     world!") == ["Hello", "world", "!"]

    # Check if the function correctly handles a message with leading and trailing spaces
    assert message_words("   Hello, world!   ") == ["Hello", ",", "world", "!"]

    # Check if the function correctly handles a message with non-English characters
    assert message_words("Hola, ¿cómo estás?") == ["Hola", ",", "¿cómo", "estás", "?"]

    # Check if the function correctly handles a message with contractions
    assert message_words("I'll be there at 5 o'clock.") == [
        "I",
        "'ll",
        "be",
        "there",
        "at",
        "5",
        "o'clock",
        ".",
    ]
