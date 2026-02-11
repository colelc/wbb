import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService
from src.service.utility_service import UtilityService

class QuarterService(object):
    def __init__(self):
        self.logger = AppLogger.get_logger()
        #self.config = config

        #self.team_id = config.get("team.id")
        self.team_ids = UtilityService.get_team_ids()

        self.output_dir = UtilityService.get_output_dir()
        #self.playbyplay_data_file = UtilityService.get_playbyplay_data_file()
        #self.playbyplay_data_dir = UtilityService.get_playbyplay_data_dir()
        self.combined_data_file = UtilityService.get_combined_data_file()
        self.combined_data_dir = UtilityService.get_combined_data_dir()

    def analysis(self):
        for teamId in self.team_ids:
            combined_data_path = os.path.join(self.output_dir, str(teamId), self.combined_data_dir)
            data_list = FileService.read_all_files_in_directory(combined_data_path)

            individual_quarter_wins = self.count_wins_by_individual_quarter(teamId, data_list)
            for k,v in individual_quarter_wins.items():
                if not "boxscores" in k:
                    self.logger.info(str(teamId) + " " + k + " -> " + str(v))
                #else:
                #    for boxscore in v:
                #        self.logger.info(k + " -> " + boxscore)

    def count_wins_by_individual_quarter(self, teamId:int, data_list, debug="N"):

        if data_list is None or len(data_list) == 0:
            return None

        games_played = 0
        q1_wins = 0
        q2_wins = 0
        q3_wins = 0
        q4_wins = 0

        for data in data_list:
            games_played += 1
            winningTeamId = data["winningTeamId"]
            homeTeamId = data["homeTeamId"]
            awayTeamId = data["awayTeamId"]
            homeTeam = data["homeTeam"]
            awayTeam = data["awayTeam"]
            quarter_scores = data["outcome"]["quarter_scores"]
            q1 = quarter_scores["q1"] 
            q2 = quarter_scores["q2"]
            q3 = quarter_scores["q3"]
            q4 = quarter_scores["q4"]

            if teamId == homeTeamId:
                q1_wins = q1_wins+1 if q1["q1_home_team_score"] >= q1["q1_away_team_score"] else q1_wins
                q2_wins = q2_wins+1 if q2["q2_home_team_score"] >= q2["q2_away_team_score"] else q2_wins
                q3_wins = q3_wins+1 if q3["q3_home_team_score"] >= q3["q3_away_team_score"] else q3_wins
                q4_wins = q4_wins+1 if q4["q4_home_team_score"] >= q4["q4_away_team_score"] else q4_wins
            elif teamId == awayTeamId:
                q1_wins = q1_wins+1 if q1["q1_away_team_score"] >= q1["q1_home_team_score"] else q1_wins
                q2_wins = q2_wins+1 if q2["q2_away_team_score"] >= q2["q2_home_team_score"] else q2_wins
                q3_wins = q3_wins+1 if q3["q3_away_team_score"] >= q3["q3_home_team_score"] else q3_wins
                q4_wins = q4_wins+1 if q4["q4_away_team_score"] >= q4["q4_home_team_score"] else q4_wins

            if debug == "Y":
                if teamId == homeTeamId:
                    if q1["q1_home_team_score"] >= q1["q1_away_team_score"]:
                        #pass
                        self.logger.info("Q1 " + homeTeam + " " + str(q1["q1_home_team_score"]) + ", " + awayTeam + " " + str(q1["q1_away_team_score"]))
                    if q2["q2_home_team_score"] >= q2["q2_away_team_score"]:
                        #pass
                        self.logger.info("Q2 " + homeTeam + " " + str(q2["q2_home_team_score"]) + ", " + awayTeam + " " + str(q2["q2_away_team_score"]))
                    if q3["q3_home_team_score"] >= q3["q3_away_team_score"]:
                        #pass
                        self.logger.info("Q3 " + homeTeam + " " + str(q3["q3_home_team_score"]) + ", " + awayTeam + " " + str(q3["q3_away_team_score"]))
                    if q4["q4_home_team_score"] >= q4["q4_away_team_score"]:
                        #pass
                        self.logger.info("Q4 " + homeTeam + " " + str(q4["q4_home_team_score"]) + ", " + awayTeam + " " + str(q4["q4_away_team_score"]))
                elif teamId == awayTeamId:
                    if q1["q1_away_team_score"] >= q1["q1_home_team_score"]:
                        #pass
                        self.logger.info("Q1 " + awayTeam + " " + str(q1["q1_away_team_score"]) + ", " + homeTeam + " " + str(q1["q1_home_team_score"]))
                    if q2["q2_away_team_score"] >= q2["q2_home_team_score"]:
                        #pass
                        self.logger.info("Q2 " + awayTeam + " " + str(q2["q2_away_team_score"]) + ", " + homeTeam + " " + str(q2["q2_home_team_score"]))
                    if q3["q3_away_team_score"] >= q3["q3_home_team_score"]:
                        #pass
                        self.logger.info("Q3 " + awayTeam + " " + str(q3["q3_away_team_score"]) + ", " + homeTeam + " " + str(q3["q3_home_team_score"]))
                    if q4["q4_away_team_score"] >= q4["q4_home_team_score"]:
                        #pass
                        self.logger.info("Q4 " + awayTeam + " " + str(q4["q4_away_team_score"]) + ", " + homeTeam + " " + str(q4["q4_home_team_score"]))

        q1_pct = round((q1_wins / games_played) * 100, 0)
        q2_pct = round((q2_wins / games_played) * 100, 0)
        q3_pct = round((q3_wins / games_played) * 100, 0)
        q4_pct = round((q4_wins / games_played) * 100, 0)

        return {
            "games_played": games_played,
            "q1": {"wins": q1_wins, "pct": q1_pct},
            "q2": {"wins": q2_wins, "pct": q2_pct},
            "q3": {"wins": q3_wins, "pct": q3_pct},
            "q4": {"wins": q4_wins, "pct": q4_pct},
        }    



    # def filter_by_losses_or_wins(self, win_or_loss, point_diff, playbyplay_list):
    #     filtered = list()

    #     for pbp in playbyplay_list:
    #         # for k,v in pbp.items():
    #         #     self.logger.info(k + " -> " + str(v))
    #         homeTeamId = pbp["homeTeamId"]
    #         awayTeamId = pbp["awayTeamId"]
    #         homeTeamScore = pbp["homeTeamPoints"]
    #         awayTeamScore = pbp["awayTeamPoints"]

    #         if pbp["available"] == "N":
    #             continue

    #         if abs(homeTeamScore - awayTeamScore) > point_diff:
    #             continue

    #         if self.team_id == homeTeamId:
    #             if win_or_loss == "L" and homeTeamScore < awayTeamScore:
    #                 filtered.append(pbp)
    #             elif win_or_loss == "W" and homeTeamScore > awayTeamScore:
    #                 filtered.append(pbp)
    #         elif self.team_id == awayTeamId:
    #             if win_or_loss == "L" and awayTeamScore < homeTeamScore:
    #                 filtered.append(pbp)
    #             elif win_or_loss == "W" and awayTeamScore > homeTeamScore:
    #                 filtered.append(pbp)

    #     return filtered
    
    # def analysis_3q(self, pbp_list):
    #     for pbp in pbp_list:
    #         #self.logger.info(str(pbp))

    #         game_date = pbp["game_date"]
    #         away_team = pbp["awayTeam"]
    #         home_team = pbp["homeTeam"]
    #         away_team_pts = pbp["awayTeamPoints"]
    #         home_team_pts = pbp["homeTeamPoints"]
            
    #         home_team_3qtr_score = pbp["end_quarter_scores"]["q3"]["q3_home_team_score"]
    #         away_team_3qtr_score = pbp["end_quarter_scores"]["q3"]["q3_away_team_score"]

    #         #print("")

    #         #print(game_date + " "  + away_team + " at "  + home_team + ": Final Score: " + " " + home_team + " " + str(home_team_pts) + " " + away_team + " " + str(away_team_pts))
    #         print(game_date + " 3Q End: " + home_team + " " + str(home_team_3qtr_score) + " " + away_team + " " + str(away_team_3qtr_score))


