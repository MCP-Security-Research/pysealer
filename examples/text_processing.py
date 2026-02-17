#!/usr/bin/env python3

# Text Processing example: String manipulation, parsing, and analysis

import re
import asyncio
from collections import Counter

def is_palindrome(text):
    """Check if a string is a palindrome (ignoring case and non-alphanumeric chars)."""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    return cleaned == cleaned[::-1]

def reverse_string(text):
    """Reverse a string."""
    return text[::-1]

def count_words(text):
    """Count the number of words in a text string."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)

async def async_word_frequency(text):
    """Async function to analyze word frequency in text."""
    await asyncio.sleep(0.1)  # Simulate async processing
    words = re.findall(r'\b\w+\b', text.lower())
    return Counter(words)

class TextAnalyzer:
    """A class for analyzing text content."""
    def __init__(self, text):
        self.text = text
    
    def word_count(self):
        """Return the total word count."""
        words = re.findall(r'\b\w+\b', self.text)
        return len(words)
    
    def char_count(self, include_spaces=True):
        """Return character count."""
        if include_spaces:
            return len(self.text)
        return len(re.sub(r'\s', '', self.text))
    
    def most_common_words(self, n=5):
        """Return the n most common words."""
        words = re.findall(r'\b\w+\b', self.text.lower())
        counter = Counter(words)
        return counter.most_common(n)

def format_snake_case(text):
    """Convert text to snake_case."""
    # Replace spaces and hyphens with underscores
    text = re.sub(r'[-\s]+', '_', text)
    # Insert underscore before capital letters and convert to lowercase
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    return text.lower()

def main():
    # Palindrome tests
    test_palindrome = "A man a plan a canal Panama"
    print(f"Is '{test_palindrome}' a palindrome? {is_palindrome(test_palindrome)}")
    print(f"Is 'hello' a palindrome? {is_palindrome('hello')}")
    
    # String reversal
    text = "Hello, World!"
    print(f"\nOriginal: {text}")
    print(f"Reversed: {reverse_string(text)}")
    
    # Word counting
    sample_text = "The quick brown fox jumps over the lazy dog. The dog was very lazy."
    print(f"\nText: '{sample_text}'")
    print(f"Word count: {count_words(sample_text)}")
    
    # Async word frequency
    freq_result = asyncio.run(async_word_frequency(sample_text))
    print(f"\nWord frequency: {dict(freq_result.most_common(5))}")
    
    # TextAnalyzer class
    analyzer = TextAnalyzer(sample_text)
    print(f"\n--- Text Analysis ---")
    print(f"Words: {analyzer.word_count()}")
    print(f"Characters (with spaces): {analyzer.char_count()}")
    print(f"Characters (no spaces): {analyzer.char_count(include_spaces=False)}")
    print(f"Most common words: {analyzer.most_common_words(3)}")
    
    # Text formatting
    original = "convert this to different cases"
    print(f"\n--- Text Formatting ---")
    print(f"Original: {original}")
    print(f"snake_case: {format_snake_case(original)}")
    
    pascal_example = "ConvertThisString"
    print(f"PascalCase '{pascal_example}' to snake_case: {format_snake_case(pascal_example)}")

if __name__ == "__main__":
    main()
