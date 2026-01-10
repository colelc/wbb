import os
import json
import itertools
from itertools import groupby
import sys
import time
import urllib.request
from collections import Counter
from src.config.config import Config
from src.logging.app_logger import AppLogger

class WordLookup(object):
    def __init__(self, word_config: dict):
        self.logger = AppLogger.get_logger()

        self.word_file_path = word_config.get("word_file_path")
        self.pairs = word_config.get("pairs")
        self.middle = word_config.get("middle")
        self.letters = word_config.get("letters")
        self.max_word_length = word_config.get("max_word_length")


    def search(self) -> dict:
        #answers = list()
        answers = dict()  # key=pair, value=list of words from word file

        for pair in self.pairs:
            answers[pair] = self.search_file(pair)

        return answers


    def search_file(self, known_two: str):
        answers = list()

        items = 0
        dictionary = set()
        with open(self.word_file_path, 'r') as f:
            for line in f:
                items += 1
                #self.logger.info (line.strip())
                dictionary.add(line.lower().strip())

        #self.logger.info(str(items) + " dictionary items")

        self.logger.info ("letters: " + str(self.letters))
        self.logger.info ("middle: " + self.middle)
        self.logger.info ("known_two: " + known_two)

        for N in range(2, self.max_word_length):
            #self.logger.info("")
            #self.logger.info(str(N) + ": TOTAL combos: " + str(total_combos))

            for combo in itertools.product(self.letters,  repeat=N):
                part = "".join(combo)
                word = known_two + part

                if not word.__contains__(self.middle):
                    continue

                #self.logger.info (word)
                if word.lower().strip() in dictionary:
                    self.logger.info (str(N+2) + ": " +  word + " is in dictionary")
                    answers.append(word)


        answers.sort()
        return answers


