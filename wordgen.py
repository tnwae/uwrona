#!/usr/bin/env python3

import uwrona_utils as uwrona
import json
import numpy as np
import sys
import re
from typing import List

try:
    with open("./wordgen_rules.json") as fp:
        raw = json.load(fp)
        consonant_freqtab = raw["consonantFrequencies"]
        vowel_freqtab = raw["vowelFrequencies"]
        phoneme_classes = raw["phonemeClasses"]
        voicing_rules = raw["voicingRules"]
        syllables = raw["permissibleSyllables"]
        replacement_rules = raw["replacementRules"]
        syllable_count_probabilities = raw["syllableLengthRules"]
except Exception as ex:
    print(ex)
    sys.exit(1)


def get_char(phoneme_class: str, vowelp: bool = False) -> str:
    if phoneme_class.isupper():
        phonemes_in_class = phoneme_classes[phoneme_class]
        freqtab = vowel_freqtab if vowelp else consonant_freqtab
        ch = ""

        while ch not in phonemes_in_class:
            ch = np.random.choice(list(freqtab.keys()),
                                  1,
                                  p=list(freqtab.values()))
        return ch[0]
    else:
        return phoneme_class


def compile_char(ch: str) -> str:
    if ch in "HLV":
        vowelp = True
    else:
        vowelp = False
    return get_char(ch, vowelp)


def make_word(syllable_count: int = 0, mode: str = "noun") -> List[str]:
    tmpl = ""
    intermediate_word = ""
    final_word = ""
    results = list()

    for i in range(0, syllable_count):
        tmpl += np.random.choice(list(syllables.keys()),
                                 1,
                                 p=list(syllables.values()))[0]

    for ch in tmpl:
        intermediate_word += compile_char(ch)

    for rule, filters in replacement_rules.items():
        for target, replacement in filters.items():
            intermediate_word = re.sub(target, replacement, intermediate_word)

    for ch in intermediate_word:
        final_word += compile_char(ch)
    
    if mode == "verb":
        results.append(final_word)
        if uwrona.is_vowel(final_word[-1]):
            inter = get_char(np.random.choice(["S", "W", "R", "P", "N"],
                                              p=[0.3, 0.3, 0.15, 0.15, 0.1]))
            results.append(final_word + f"{inter}en")
        else:
            inter = voicing_rules.get(final_word[-1], "n")
            results.append(final_word[:-1] + inter + "en")
    elif mode == "noun":
        results.append(final_word)
    elif mode == "name":
        results.append(final_word.capitalize())

    return sorted(results)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("wordgen")
    parser.add_argument("-c",
                        "--count",
                        help="number of words to generate",
                        type=int,
                        default=1)
    parser.add_argument("-m",
                        "--max-length",
                        help="maximum number of syllables",
                        type=int,
                        default=-1)
    parser.add_argument("-M",
                        "--min-length",
                        help="minimum number of syllables",
                        type=int,
                        default=1)
    parser.add_argument("-t",
                        "--type",
                        help="type of word to generate (noun|name|verb)",
                        type=str,
                        default="noun")
    args = parser.parse_args()

    count = args.count
    mode = args.type
    randomp = (args.max_length == -1)
    min_length = args.min_length
    max_length = args.max_length + 1
    result = set()

    for i in range(count):
        if randomp:
            length = np.random.choice(list(range(1, len(syllable_count_probabilities))),
                                      p=syllable_count_probabilities[1:])
        else:
            length = np.random.choice(list(range(min_length, max_length)))

        for word in make_word(length, mode):
            result.add(word)
    
    if mode != "verb":
        result = [word for word in result if word[-2:] != "en"]
    
    for word in sorted(result):
        print(word)
