#!/usr/bin/env python3

import json
import sys
from typing import Tuple

action_table = {
    "W": (lambda v, _: counterparts[v]),
    "V": (lambda v, _: v),
    "C": (lambda _, c: c),
    "X": (lambda _, c: voicings.get(c, c))
}

try:
    with open("./rules.json", "r") as fp:
        raw = json.load(fp)
        noun_templates = raw["declensionTable"]
        counterparts = raw["vowelHarmonyRules"]
        voicings = raw["voicingRules"]
        verb_templates = raw["inflectionTable"]
except FileNotFoundError as ex:
    print(ex)
    sys.exit(1)


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


def derive_word_parts(word: str, elider: str) -> Tuple[str, str, str]:
    if len(word) == 2:
        if is_vowel(word[0]):
            vowel = word[0]
            consonant = word[1]
        else:
            vowel = word[1]
            consonant = word[0]

        root = vowel if is_vowel(word[0]) else consonant
        ending = consonant if is_vowel(word[0]) else vowel
    else:
        root, ending = get_word_ending(word)
        if len(ending) == 1:
            vowel = ending
            consonant = elider
        else:
            vowel = ending[0]
            consonant = ending[1]

    if len(word) == 2 and is_vowel(word[0]):
        inflected_word = ""
    else:
        inflected_word = root

    return vowel, consonant, inflected_word


def inflect_noun(word: str) -> dict:
    """
  Inflect the given word according to the rule table resident
  in memory.

  :param: word the word to inflect
  :return: a dict keyed on noun case containing inflections of the word passed in
  """
    root, ending = get_word_ending(word)
    cases = list(noun_templates.keys())
    inflections = dict()

    for word_case in cases:
        vowel, consonant, inflected_word = derive_word_parts(
            word, noun_templates[word_case]["elide"])

        tmpl = noun_templates[word_case]["rule"]

        if tmpl == "@":
            inflections[word_case] = word
            continue

        for ch in tmpl:
            if ch.isupper():
                action = action_table.get(ch, None)

                if action:
                    inflected_word += action(vowel, consonant)
                else:
                    raise KeyError(f"invalid action type {action}")
            else:
                inflected_word += ch

        inflections[word_case] = inflected_word

    return inflections


def inflect_verb(word: str) -> dict:
    """
      Inflect the given word according to the rule table resident
      in memory.
    
      :param: word the word to inflect
      :return: a dict keyed on verb aspect containing inflections of the word passed in
    """
    root, ending = get_word_ending(word)
    moods = list(verb_templates.keys())
    inflections = dict()

    for mood in moods:
        if mood not in inflections:
            inflections[mood] = {}

        for tense in verb_templates[mood]:
            if tense not in inflections[mood]:
                inflections[mood][tense] = {}

            for aspect in verb_templates[mood][tense]:
                if aspect not in inflections[mood][tense]:
                    inflections[mood][tense][aspect] = {}

                vowel, consonant, inflected_word = derive_word_parts(
                    word, verb_templates[mood][tense][aspect]["elide"])

                tmpl = verb_templates[mood][tense][aspect]["rule"]

                for ch in tmpl:
                    if ch.isupper():
                        action = action_table.get(ch, None)

                        if action:
                            inflected_word += action(vowel, consonant)
                        else:
                            raise KeyError(f"invalid action type {action}")
                    else:
                        inflected_word += ch

                inflections[mood][tense][aspect] = inflected_word

    return inflections


if __name__ == "__main__":
    import argparse

    inflectors = {"v": inflect_verb, "n": inflect_noun}

    parser = argparse.ArgumentParser("inflector")
    parser.add_argument("word", help="word to inflect", type=str)
    parser.add_argument("-t",
                        "--type",
                        help="type of inflection to perform",
                        type=str,
                        default="n")
    args = parser.parse_args()

    inflector = inflectors[args.type]
    inflected_word = inflector(args.word)

    if args.type == 'n':
        for word_case, word in inflected_word.items():
            print(f"{word_case:15}{word}")
    elif args.type == 'v':
        for mood, tenses in inflected_word.items():
            print(f"{mood}:")
            for tense, aspects in tenses.items():
                print(f"\t{tense}:")
                for aspect, conjugation in aspects.items():
                    print(f"\t\t{aspect:10}:  {conjugation}")
        print("""
Additional markings in their proper order:

    Evidentials: add one of the following prefixes:
        - Firsthand: ja(j)-
        - Hearsay: cur(e)-
        - Story/legend: zu(j)-
        - Inferential: jur(e)-
        - Neutral: <no marker>
    
    Other aspects:
        - Obligative - add ge(t)- prefix to the potential
        - Imperative - add be(t)- prefix to the present indicative
        - Presumptive - add wu(r)- prefix to the conditional
        - Imitative - add ren(i)- prefix to the any other aspect
        - Volitional - add xi(r)- prefix to the potential
    
    Interrogative:
        Add the -(i)ka suffix.
    
    Negation:
        Add the -(a)pa suffix.""")
