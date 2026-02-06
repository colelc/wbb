import json
import re
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class ModelCoaching(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.config = config

        self.output_dir = config.get("output.data.dir")
        metadata_file = config.get("metadata.file")
        self.metadata_file_path = os.path.join(self.output_dir, metadata_file)

        self.seasons = [season.strip() for season in config.get("seasons").split(",")]
        self.team_id = config.get("team.id")

        # use the box score data to get home/away teams
        self.boxscore_data_file = config.get("boxscore.data.file")
        self.boxscore_data_path = os.path.join(self.output_dir, "boxscore")
        self.boxscore_data = FileService.read_all_files_in_directory(self.boxscore_data_path)

        self.playbyplay_data_file = config.get("playbyplay.data.file")
        self.playbyplay_data_path = os.path.join(self.output_dir, "playbyplay")
        os.makedirs(self.playbyplay_data_path, exist_ok=True)

    def model(self):
        pass

