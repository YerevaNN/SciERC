#!/usr/bin/env python

import sys
import json


def get_char_vocab(input_filenames, output_filename):
  vocab = set()
  for filename in input_filenames:
    with open(filename, "r", encoding="utf-8") as f:
      for line in f.readlines():
        for sentence in json.loads(line)["sentences"]:
          for word in sentence:
            vocab.update(word)
  vocab = sorted(list(vocab))
  with open(output_filename, "w", encoding="utf-8") as f:
    for char in vocab:
      f.write(u"{}\n".format(char))
  print(("Wrote {} characters to {}".format(len(vocab), output_filename)))


get_char_vocab(["../data/sciie.{}.jsona".format(partition) for partition in ("train", "dev")], "char_vocab.english.txt")

