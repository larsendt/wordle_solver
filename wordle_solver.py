#!/usr/bin/env python

import logging
import random
import re
import sys

USAGE = """\
Usage: {} spec [spec..]
Enter one spec per guess you've made so far
    For example {} 'we!ar?y' 'te!nor?' 've!r?ve' 'r!e!ads!'

Spec: 'we!ar?y'
    ! = correct letter/spot
    ? = correct letter/incorrect spot
    no suffix = mismatch

Tip: surround each spec in single quotes to prevent bash from interpreting the '!'s\
"""

logging.basicConfig(level=logging.INFO)
LETTERS = "abcdefghijklmnopqrstuvwxyz"
SPEC_RE = r"([a-z][!?]? *){5}"
LETTER_RE = r"[a-z][!?]? *"


class Spec(object):
    def __init__(self, spec_str):
        self.spec_str = spec_str
        self.locations = []
        self.non_locations = []
        self.non_characters = []

        if not re.fullmatch(SPEC_RE, spec_str):
            raise ValueError("Spec must match {}".format(SPEC_RE))

        tmp_non_chars = []
        matches = re.findall(LETTER_RE, spec_str)
        for i, m in enumerate(matches):
            m = m.strip()
            if len(m) == 1:
                tmp_non_chars.append((m, i))
            elif len(m) == 2 and m[1] == "!":
                self.locations.append((m[0], i))
            elif len(m) == 2 and m[1] == "?":
                self.non_locations.append((m[0], i))
            else:
                raise AssertionError("Spec '{}' was invalid??".format(spec_str))

        location_chars = {c: i for c, i in self.locations}
        for c, i in tmp_non_chars:
            if c in location_chars:
                self.non_locations.append((c, i))
            else:
                self.non_characters.append(c)

        logging.debug("Spec for '{}':".format(spec_str))
        logging.debug("\tLocations: {}".format(self.locations))
        logging.debug("\tNon-locations: {}".format(self.non_locations))
        logging.debug("\tNon-characters: {}".format(self.non_characters))

    def matches(self, word):
        logging.debug("Testing word '%s' against spec '%s'", word, self.spec_str)
        matched_locations = {}

        for c, i in self.locations:
            if word[i] == c:
                matched_locations[c] = i
            else:
                logging.debug("DQ: word[%d] was %s, but spec wants %s", i, word[i], c)
                return False

        for c, i in self.non_locations:
            if word[i] == c:
                logging.debug(
                    "DQ: word[%d] was %s, but spec knows that location mismatches",
                    i,
                    word[i],
                    c,
                )
                return False
            elif not c in word:
                logging.debug(
                    "DQ: %s not found in word, but spec has it",
                    c,
                )
                return False

        for c in self.non_characters:
            if c in word:
                logging.debug("DQ: %s known not to be in target", c)
                return False

        logging.debug("Word '%s' matches spec '%s'", word, self.spec_str)
        return True


class Specs(object):
    def __init__(self, spec_strs):
        self.specs = [Spec(s) for s in spec_strs]

    def matches(self, word):
        word = word.lower()

        if len(word) != 5:
            logging.debug("DQ: length not 5")
            return False

        if not word.isalpha():
            return False

        for spec in self.specs:
            if not spec.matches(word):
                return False
        return True


def main():
    if len(sys.argv) == 1:
        print(USAGE.format(sys.argv[0], sys.argv[0]))
        return

    spec = Specs(sys.argv[1:])

    matches = [word.strip() for word in open("words") if spec.matches(word.strip())]
    random.shuffle(matches)

    if len(matches) == 0:
        print("No matches found")
        return

    if len(matches) > 10:
        print("{} matches found, here's 10:".format(len(matches)))
    else:
        print("{} matches found:".format(len(matches)))

    for match in matches[:10]:
        print(match)


if __name__ == "__main__":
    main()
