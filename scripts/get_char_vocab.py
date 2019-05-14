#!/usr/bin/env python

import sys
import json


def get_char_vocab(input_filenames, output_filename):
  vocab = set()
  for filename in input_filenames:
    with open(filename) as f:
      for line in f.readlines():
        for sentence in json.loads(line)["sentences"]:
          for word in sentence:
            vocab.update(word)
  vocab = sorted(list(vocab))
  with open(output_filename, "w", encoding="utf-8") as f:
    for char in vocab:
      f.write(u"{}\n".format(char)) #.encode("utf8"))
  print("Wrote {} characters to {}".format(len(vocab), output_filename))


# get_char_vocab(["./data/processed_data/json/{}.json".format(partition) for partition in ("train", "dev", "test")], "char_vocab.english.txt")

### HARDCODEEE
print("Doing HARDCODED STUFF!!!")
assert(False)
get_char_vocab(["../1.0alpha4.train.DS0.2.eps0.5.bottom1400.json",
                "../1.0alpha4.dev.scierc.json",
                "../1.0alpha4.test.scierc.json"], "char_vocab.english.txt")
print("Some HARDCODED STUFF DONE!!!")

