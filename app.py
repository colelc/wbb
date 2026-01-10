import os
from src.config.config import Config
from src.logging.app_logger import AppLogger
from src.service.scraper import Scraper
from src.service.boxscore_service import BoxscoreService


class App(object):

    @classmethod
    def go(cls):

        logger = AppLogger.set_up_logger("app.log")
        config = Config.set_up_config(".env")

        #games = Scraper(config).scrape()
        Scraper(config).scrape()

        # build the W-L data
        BoxscoreService(config).collect_boxscore_data()
         

        #for k,v in games.items():
        #    logger.info(k + " -> " + str(v))



        # word_config = {
        #     "word_file_path" : os.path.join(config.get("input.data.dir"), config.get("word.file")),
        #     "pairs": data["pairs"],
        #     "middle": data["middle"],
        #     "letters":  data["letters"],
        #     "max_word_length": int(config.get("max.word.length")) or 9
        # }






App.go()