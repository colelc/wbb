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

        filtered_boxscore_list = list()

        if win_or_loss == "L":
            losses = self.get_losses(boxscore_list)
            if len(losses) > 0:
                filtered_boxscore_list = self.filter_losses_by_margin(losses, 5, "less")
        else:
            wins = self.get_wins(boxscore_list)
            if len(wins) > 0:
                filtered_boxscore_list = self.filter_wins_by_margin(wins, 5, "less")
        
        # for bs in filtered_boxscore_list:
        #     self.logger.info(str(bs["winningTeam"]))
        #     self.logger.info(str(bs["losingTeam"]))

        self.freethrow_analyis(filtered_boxscore_list, win_or_loss)
    
    def get_losses(self, boxscore_list):
        return list(filter(lambda x: x["losingTeamId"] == self.team_id, boxscore_list))
    
    def get_wins(self, boxscore_list):
        return list(filter(lambda x: x["winningTeamId"] == self.team_id, boxscore_list))
    
    def filter_losses_by_margin(self, losing_list, margin, moreOrLess):
        if moreOrLess == "more":
            return list(filter(lambda x: abs(x["losingTeam"]["margin"]) > abs(margin), losing_list))
        else:
            return list(filter(lambda x: abs(x["losingTeam"]["margin"]) <= abs(margin), losing_list))
    
    def filter_wins_by_margin(self, winning_list, margin, moreOrLess):
        if moreOrLess == "more":
            return list(filter(lambda x: abs(x["winningTeam"]["margin"]) > abs(margin), winning_list))
        else:
            return list(filter(lambda x: abs(x["winningTeam"]["margin"]) <= abs(margin), winning_list))

    def freethrow_analyis(self, boxscore_list, win_or_lose):
        for bs in boxscore_list:
            print("")
            #self.logger.info(str(bs))
            game_date = bs["game_date"]
            home_team = bs["homeTeam"]["team"]
            home_team_pts = str(bs["homeTeam"]["PTS"])
            homeTeam_ft = bs["homeTeam"]["FT"]
            homeTeam_fta = bs["homeTeam"]["FTA"]
            homeTeam_assists = bs["homeTeam"]["AST"]
            homeTeam_turnovers = bs["homeTeam"]["TO"]

            away_team = bs["awayTeam"]["team"]
            away_team_pts = str(bs["awayTeam"]["PTS"])
            awayTeam_ft = bs["awayTeam"]["FT"]
            awayTeam_fta = bs["awayTeam"]["FTA"]
            awayTeam_assists = bs["awayTeam"]["AST"]
            awayTeam_turnovers = bs["awayTeam"]["TO"]

            pt_diff = str(abs(bs["awayTeam"]["PTS"] - bs["homeTeam"]["PTS"]))

            print(game_date + " "  + away_team + " at "  + home_team + ": Final Score: " + home_team_pts + "-" + away_team_pts)


            print(game_date + " " + home_team + " FT-FTA: " + str(homeTeam_ft) + "-" + str(homeTeam_fta))
            print(game_date + " " + away_team + " FT-FTA: " + str(awayTeam_ft) + "-" + str(awayTeam_fta))

            #print(game_date + " " + home_team + " Assist/Turnover ratio: " + str(homeTeam_assists) + "/" + str(homeTeam_turnovers))
            #print(game_date + " " + away_team + " Assist/Turnover ratio: " + str(awayTeam_assists) + "/" + str(awayTeam_turnovers))





