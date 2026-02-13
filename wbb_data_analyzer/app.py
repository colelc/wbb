import os
from src.config.config import Config
from src.logging.app_logger import AppLogger
from src.model.model_coaching import ModelCoaching
from src.service.scrape.scraper import Scraper
from src.service.freethrow_service import FreethrowService
from src.service.quarter_service import QuarterService
from src.service.win_service import WinService
from src.service.file_service import FileService
from src.service.utility_service import UtilityService


class App(object):

    @classmethod
    def go(cls):

        FileService.delete_file("app.log")

        logger = AppLogger.set_up_logger("app.log")
        config = Config.set_up_config(".env")
        UtilityService.set_up_config(config)

        Scraper(config)

        # start running models
        #ModelCoaching().model()

        # analyze FT percentages, losses 5 points or less
        #FreethrowService().analyze_close_game_ft_percentages("L")
        #FreethrowService().analyze_close_game_ft_percentages("W")

        # analyze percentage wins by combinations of quarters in which a team outscores its opponent
        #QuarterService().analysis()

        WinService().analysis()

App.go()