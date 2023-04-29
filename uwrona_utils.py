#!/usr/bin/env python3

from typing import Tuple

def is_vowel(ch: str) -> bool:
    """Determine if a given character is a vowel.
    
    :param: ch the character to test
    :return: True if the character is a vowel, False otherwise"""
    if len(ch) > 1:
        raise RuntimeError("argument to is_vowel too long")

    return ch in "aeiouy"


def get_word_ending(word: str) -> Tuple[str, str]:
    """Return the ending of the word - the final vowel if the
     word ends with a vowel and the final consonant and vowel
     if not.
     
     :param: word the word to retrieve the ending from
     :return: the word's root and ending as a tuple"""
    if len(word) < 2:
        raise RuntimeError("argument to get_word_ending too short")

    if len(word) == 2:
        if is_vowel(word[0]):
            return word[0], word[1]
        else:
            return word[1], word[0]

    if is_vowel(word[-1]):
        return word[:-1], word[-1]
    else:
        return word[:-2], word[-2:]


def harmonize(word: str, nucleus_vowel: str) -> str:
    harmonized_word = word
    for ch in word:
        if is_vowel(ch):
            harmonized_word = harmonized_word.replace(ch, nucleus_vowel)

    return harmonized_word

