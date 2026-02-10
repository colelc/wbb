import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService
from src.service.utility_service import UtilityService

class End3QtrService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.config = config

        #self.team_id = config.get("team.id")
        self.team_ids = UtilityService.get_team_ids(config)

        self.output_dir = config.get("output.data.dir")
        self.playbyplay_data_file = config.get("playbyplay.data.file")
        self.playbyplay_data_path = os.path.join(self.output_dir, "playbyplay")

    def analyze_after_3_quarters(self, win_or_loss):
        # collect the playbyplay data
        playbyplay_list = FileService.read_all_files_in_directory(self.playbyplay_data_path)

        filtered_playbyplay_list = self.filter_by_losses_or_wins(win_or_loss, 5, playbyplay_list)
        #for bs in filtered_boxscore_list:
        #    self.logger.info(str(bs))

        self.analysis_3q(filtered_playbyplay_list)


    def filter_by_losses_or_wins(self, win_or_loss, point_diff, playbyplay_list):
        filtered = list()

        for pbp in playbyplay_list:
            # for k,v in pbp.items():
            #     self.logger.info(k + " -> " + str(v))
            homeTeamId = pbp["homeTeamId"]
            awayTeamId = pbp["awayTeamId"]
            homeTeamScore = pbp["homeTeamPoints"]
            awayTeamScore = pbp["awayTeamPoints"]

            if pbp["available"] == "N":
                continue

            if abs(homeTeamScore - awayTeamScore) > point_diff:
                continue

            if self.team_id == homeTeamId:
                if win_or_loss == "L" and homeTeamScore < awayTeamScore:
                    filtered.append(pbp)
                elif win_or_loss == "W" and homeTeamScore > awayTeamScore:
                    filtered.append(pbp)
            elif self.team_id == awayTeamId:
                if win_or_loss == "L" and awayTeamScore < homeTeamScore:
                    filtered.append(pbp)
                elif win_or_loss == "W" and awayTeamScore > homeTeamScore:
                    filtered.append(pbp)

        return filtered
    
    def analysis_3q(self, pbp_list):
        for pbp in pbp_list:
            #self.logger.info(str(pbp))

            game_date = pbp["game_date"]
            away_team = pbp["awayTeam"]
            home_team = pbp["homeTeam"]
            away_team_pts = pbp["awayTeamPoints"]
            home_team_pts = pbp["homeTeamPoints"]
            
            home_team_3qtr_score = pbp["end_quarter_scores"]["q3"]["q3_home_team_score"]
            away_team_3qtr_score = pbp["end_quarter_scores"]["q3"]["q3_away_team_score"]

            #print("")

            #print(game_date + " "  + away_team + " at "  + home_team + ": Final Score: " + " " + home_team + " " + str(home_team_pts) + " " + away_team + " " + str(away_team_pts))
            print(game_date + " 3Q End: " + home_team + " " + str(home_team_3qtr_score) + " " + away_team + " " + str(away_team_3qtr_score))


