import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService
from src.service.utility_service import UtilityService

class WinService(object):
    def __init__(self):
        self.logger = AppLogger.get_logger()

        self.head_to_head = UtilityService.get_head_to_head_teams()

        self.output_dir = UtilityService.get_output_dir()
        self.combined_data_file = UtilityService.get_combined_data_file()
        self.combined_data_dir = UtilityService.get_combined_data_dir()

    def analysis(self):
        if len(self.head_to_head) != 2:
            self.logger.error("need 2 teams for head-to-head competition analysis")
            return
        
        t1 = self.head_to_head[0]
        t2 = self.head_to_head[1]

        combined_data_path = os.path.join(self.output_dir, str(t1), self.combined_data_dir)
        data_list = FileService.read_all_files_in_directory(combined_data_path)

        t1Wins = 0
        t2Wins = 0
        games = list()

        for data in data_list:
            homeTeamId = data["homeTeamId"]
            awayTeamId = data["awayTeamId"]

            if (t1 == homeTeamId and t2 == awayTeamId) or (t1 == awayTeamId and t2 == homeTeamId):
                winningTeamId = data["winningTeamId"]
                if t1 == winningTeamId:
                    t1Wins += 1
                else:
                    t2Wins += 1

                outcome = data["outcome"]
                meta = {
                    "game_date": data["game_date"], 
                    "homeTeam": data["homeTeam"], 
                    "awayTeam": data["awayTeam"],
                    "score": outcome["winningTeam"] + " " + str(outcome["winningTeamPoints"]) + ", " + outcome["losingTeam"] + " " + str(outcome["losingTeamPoints"])
                }
                games.append(meta)

        self.logger.info(str(t1) + " wins: " + str(t1Wins))
        self.logger.info(str(t2) + " wins: " + str(t2Wins))

        for g in games:
            self.logger.info(str(g))

