import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class FreethrowService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.espn_url = config.get("espn.url")
        self.season_results_url = config.get("season.results.url")
        self.seasons = [season.strip() for season in config.get("seasons").split(",")]
        self.output_dir = config.get("output.data.dir")
        self.scrape_file = config.get("scrape.file")
        self.scrape_boxscore_file = config.get("scrape.boxscore.file")

        scrape_path = os.path.join(self.output_dir, "scrape")
        os.makedirs(scrape_path, exist_ok=True)
        for season in self.seasons:
            os.makedirs(os.path.join(scrape_path, str(season)), exist_ok=True)

        self.config = config

