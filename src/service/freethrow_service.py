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
        self.team_id = config.get("team.id")

        self.config = config

    def analyze_close_game_ft_percentages(self, win_or_loss):
        # collect the boxscore data
        boxscore_list = FileService.read_all_files_in_directory(self.boxscore_data_path)

        filtered_boxscore_list = self.filter_by_losses_or_wins(win_or_loss, 5, boxscore_list)
        #for bs in filtered_boxscore_list:
        #    self.logger.info(str(bs))

        self.freethrow_analyis(filtered_boxscore_list, win_or_loss)


    def filter_by_losses_or_wins(self, win_or_loss, point_diff, boxscore_list):
        filtered = list()

        for boxscore in boxscore_list:
            # for k,v in boxscore.items():
            #     self.logger.info(k + " -> " + str(v))

            home_score = boxscore["homeTeam"]["PTS"]
            away_score = boxscore["awayTeam"]["PTS"]
            homeTeamId = boxscore["homeTeamId"]
            awayTeamId = boxscore["awayTeamId"]

            if abs(home_score - away_score) > point_diff:
                continue

            if self.team_id == homeTeamId:
                if win_or_loss == "L" and home_score < away_score:
                    filtered.append(boxscore)
                elif win_or_loss == "W" and home_score > away_score:
                    filtered.append(boxscore)
            elif self.team_id == awayTeamId:
                if win_or_loss == "L" and away_score < home_score:
                    filtered.append(boxscore)
                elif win_or_loss == "W" and away_score > home_score:
                    filtered.append(boxscore)

        return filtered
    
    def freethrow_analyis(self, boxscore_list, win_or_lose):
        if win_or_lose != "L":
            return
        
        for bs in boxscore_list:
            self.logger.info(str(bs))
            homeTeam = bs["homeTeam"]["team"]
            homeTeam_ft = bs["homeTeam"]["FT"]
            homeTeam_fta = bs["homeTeam"]["FTA"]
            self.logger.info("homeTeam: " + homeTeam + " " + str(homeTeam_ft) + "-" + str(homeTeam_fta))

            awayTeam = bs["awayTeam"]["team"]
            awayTeam_ft = bs["awayTeam"]["FT"]
            awayTeam_fta = bs["awayTeam"]["FTA"]
            self.logger.info("awayTeam: " + awayTeam + " " + str(awayTeam_ft) + "-" + str(awayTeam_fta))





