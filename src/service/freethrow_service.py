import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class FreethrowService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.output_dir = config.get("output.data.dir")
        self.boxscore_data_file = config.get("boxscore.data.file")
        self.boxscore_data_path = os.path.join(self.output_dir, "boxscore")

        self.config = config

    def analyze_close_game_ft_percentages(self, win_or_loss):
        # collect the boxscore data
        boxscore_list = FileService.read_all_files_in_directory(self.boxscore_data_path)

        filtered_boxscore_list = self.filter_by_losses_or_wins(win_or_loss, boxscore_list)


    def filter_by_losses_or_wins(self, win_or_loss, boxscore_list):
        for b in boxscore_list:
            pass
            # for k,v in b.items():
            #     self.logger.info(k + " -> " + str(v))




