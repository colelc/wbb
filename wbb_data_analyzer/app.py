import os
from src.config.config import Config
from src.logging.app_logger import AppLogger
from src.model.model_coaching import ModelCoaching
from src.service.scrape.scraper import Scraper
from src.service.freethrow_service import FreethrowService
from src.service.end_3qtr_service import End3QtrService
from src.service.file_service import FileService


class App(object):

    @classmethod
    def go(cls):

        FileService.delete_file("app.log")

        logger = AppLogger.set_up_logger("app.log")
        config = Config.set_up_config(".env")

        Scraper(config)

        # start running models
        #ModelCoaching().model()

        # analyze FT percentages, losses 5 points or less
        #FreethrowService(config).analyze_close_game_ft_percentages("L")
        #FreethrowService(config).analyze_close_game_ft_percentages("W")

        #End3QtrService(config).analyze_after_3_quarters("L")

App.go()