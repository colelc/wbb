import re
import os
from datetime import datetime
from bs4 import BeautifulSoup
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class BoxscoreService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.output_dir = config.get("output.data.dir")
        metadata_file = config.get("metadata.file")
        self.logger.info(str(metadata_file))
        self.metadata_file_path = os.path.join(self.output_dir, metadata_file)
        self.logger.info(str(self.metadata_file_path))
        self.seasons = [season.strip() for season in config.get("seasons").split(",")]

    def collect_boxscore_data(self):
        self.logger.info(str(self.metadata_file_path))
        games_list = FileService.read_file(self.metadata_file_path)
        for game in games_list:
            #self.logger.info(str(game))
            boxscore_file = game["boxscore_file"]
            team_data = self.process_boxscore_file(boxscore_file)

    def process_boxscore_file(self, boxscore_file:str):
        with open(boxscore_file, "r", encoding="utf8") as file:
            soup = BeautifulSoup(file, "html.parser")
            #self.logger.info(str(soup))

            teams = soup.select("div.Boxscore.flex.flex-column:has(.Boxscore__Title)")
            results = []
            for team in teams:
                results.append(self.extract_team_totals(team))

            for name, stats in results:
                self.logger.info(name + " " + str(stats))

            return results
        
    def extract_team_totals(self, team_block):
        team_name = team_block.select_one(".BoxscoreItem__TeamName").get_text(strip=True)
        
        scroller = team_block.select_one("div.Table__Scroller table")
        if not scroller:
            return team_name, None
        
        all_rows = scroller.select("tbody tr")
        if len(all_rows) < 10:  # Basic sanity check
            return team_name, None
        
        # Team totals are 2nd-to-last row (index -2)
        totals_row = all_rows[-2]
        cells = [td.get_text(strip=True) for td in totals_row.select("td")]
        
        # Just verify it has the expected structure (empty first cell, PTS in second)
        if len(cells) >= 13 and not cells[0] and cells[1] and cells[1].isdigit():
            return team_name, cells[1:]  # drop leading empty entry
        
        return team_name, None


        
  