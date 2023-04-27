#!/usr/bin/env python3

import json
import numpy as np
import sys
import re

try:
    with open("./wordgen_rules.json") as fp:
        raw = json.load(fp)
        consonant_freqtab = raw["consonantFrequencies"]
        vowel_freqtab = raw["vowelFrequencies"]
        phoneme_classes = raw["phonemeClasses"]
        voicing_rules = raw["voicingRules"]
        syllables = raw["permissibleSyllables"]
        replacement_rules = raw["replacementRules"]
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


def make_word(syllable_count: int = 0) -> str:
    tmpl = ""
    intermediate_word = ""
    final_word = ""

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

    return final_word


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("wordgen")
    parser.add_argument("-c",
                        "--count",
                        help="number of words to generate",
                        type=int,
                        default=1)
    args = parser.parse_args()

    count = args.count

    for i in range(count):
        length = np.random.choice(
            [1, 2, 3, 4, 5, 6, 7, 8],
            1,
            p=[0.13, 0.18, 0.44, 0.1, 0.06, 0.04, 0.03, 0.02])
        count = length[0]
        print(make_word(count))
