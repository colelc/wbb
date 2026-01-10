import os
import itertools
from src.config.config import Config
from src.logging.app_logger import AppLogger
from src.service.scraper import Scraper
from src.service.word_lookup import WordLookup

class App(object):

    @classmethod
    def go(cls):

        logger = AppLogger.set_up_logger("app.log")
        config = Config.set_up_config(".env")

        data = Scraper(config).scrape()

        # word_config = {
        #     "word_file_path" : os.path.join(config.get("input.data.dir"), config.get("word.file")),
        #     "pairs": data["pairs"],
        #     "middle": data["middle"],
        #     "letters":  data["letters"],
        #     "max_word_length": int(config.get("max.word.length")) or 9
        # }

        # for k,v in word_config.items():
        #     logger.info(k + " -> " + str(v))

        # answers = WordLookup(word_config).search()
        # for pair, answer_list in answers.items():
        #     for answer in answer_list:
        #         logger.info(pair + " -> " + answer)




App.go()