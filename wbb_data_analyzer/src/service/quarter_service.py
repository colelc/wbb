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

        self.team_ids = UtilityService.get_team_ids()

        self.output_dir = UtilityService.get_output_dir()
        self.combined_data_file = UtilityService.get_combined_data_file()
        self.combined_data_dir = UtilityService.get_combined_data_dir()

        self.quarter_combos = [
                                [1], [2], [3], [4],
                                [1,2], [1,3], [1,4], [2,3], [2,4],
                                [1,2,3], [1,2,4], [2,3,4],
                                [1,2,3,4]
                            ]

    def analysis(self):
        for teamId in self.team_ids:
            combined_data_path = os.path.join(self.output_dir, str(teamId), self.combined_data_dir)
            data_list = FileService.read_all_files_in_directory(combined_data_path)

            #individual_quarter_wins = self.count_wins_by_individual_quarter(teamId, data_list)
            self.count_wins_by_quarter_combos(teamId, data_list)


    def count_wins_by_quarter_combos(self, teamId:int, data_list, debug="N"):

        if data_list is None or len(data_list) == 0:
            return None
        
        combo_dict = dict()
        for combo in self.quarter_combos:
            combo_dict["".join(map(str,combo))] = {
                "combo_wins": 0,
                "game_wins": 0,
                "pct": 0,
                "meta": []
            }

        retList = list()
        games_played = 0
        wins = 0

        for data in data_list:
            #self.logger.info(str(data))
            #self.logger.info(str(data["game_date"]) + " " + data["awayTeam"] + " at " + data["homeTeam"])
            outcome = data["outcome"]
            meta = {
                "game_date": data["game_date"], 
                "homeTeam": data["homeTeam"], 
                "awayTeam": data["awayTeam"],
                "score": outcome["winningTeam"] + " " + str(outcome["winningTeamPoints"]) + ", " + outcome["losingTeam"] + " " + str(outcome["losingTeamPoints"])
            }
            win_quarters = list()
            games_played += 1
            winningTeamId = data["winningTeamId"]
            if winningTeamId == teamId:
                wins += 1
            homeTeamId = data["homeTeamId"]
            awayTeamId = data["awayTeamId"]
            homeTeam = data["homeTeam"]
            awayTeam = data["awayTeam"]
            quarter_scores = data["outcome"]["quarter_scores"]
            q1 = quarter_scores["q1"] 
            q2 = quarter_scores["q2"]
            q3 = quarter_scores["q3"]
            q4 = quarter_scores["q4"]
            
            win_quarters = []

            if teamId == homeTeamId:
                if q1["q1_home_team_score"] >= q1["q1_away_team_score"]:
                    win_quarters.append(1)
                if q2["q2_home_team_score"] >= q2["q2_away_team_score"]:
                    win_quarters.append(2)
                if q3["q3_home_team_score"] >= q3["q3_away_team_score"]:
                    win_quarters.append(3)
                if q4["q4_home_team_score"] >= q4["q4_away_team_score"]:
                    win_quarters.append(4)
            elif teamId == awayTeamId:
                if q1["q1_away_team_score"] >= q1["q1_home_team_score"]:
                     win_quarters.append(1)
                if q2["q2_away_team_score"] >= q2["q2_home_team_score"]:
                     win_quarters.append(2)
                if q3["q3_away_team_score"] >= q3["q3_home_team_score"]:
                     win_quarters.append(3)
                if q4["q4_away_team_score"] >= q4["q4_home_team_score"]:
                     win_quarters.append(4)

            self.debug_output(debug, teamId, homeTeamId, homeTeam, awayTeamId, awayTeam, q1, q2, q3, q4)

            #self.logger.info("win_quarters: " + str(win_quarters))
            #self.logger.info("self.quarter_combos: " + str(self.quarter_combos))

            winners = list(filter(lambda x: set(x) == set(win_quarters), self.quarter_combos))
            #self.logger.info("winners: " + str(winners))
            if len(winners) == 0 or len(winners) != 1:
                continue

            winning_quarters = "".join(map(str, winners[0]))
            #self.logger.info("winning_quarters: " + str(winning_quarters))

            key = "".join(map(str, winners[0]))
            combo_dict[key]["combo_wins"] = combo_dict[key]["combo_wins"] + 1
            if teamId == winningTeamId:
                combo_dict[key]["game_wins"] = combo_dict[key]["game_wins"] + 1
                combo_dict[key]["meta"].append(meta)
            
            combo_dict[key]["pct"] = round((combo_dict[key]["game_wins"] / combo_dict[key]["combo_wins"]) * 100, 0)

            # for k,v in combo_dict.items():
            #     self.logger.info(k + " -> " + str(v))

        for k,dct in combo_dict.items():
            for kk,vv in dct.items():
                if kk != "meta":
                    self.logger.info(k + " " + kk + " -> " + str(vv))
            # else:
            #     meta_lst = dct[kk]
            #     for m in meta_lst:
            #         self.logger.info(str(m))



    def count_wins_by_individual_quarter(self, teamId:int, data_list, debug="N"):

        if data_list is None or len(data_list) == 0:
            return None

        games_played = 0
        q1_wins = 0
        q2_wins = 0
        q3_wins = 0
        q4_wins = 0
        wins = 0

        for data in data_list:
            games_played += 1
            winningTeamId = data["winningTeamId"]
            if winningTeamId == teamId:
                wins += 1
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

            self.debug_output(debug, teamId, homeTeamId, homeTeam, awayTeamId, awayTeam, q1, q2, q3, q4)

        q1_pct = round((q1_wins / games_played) * 100, 0)
        q2_pct = round((q2_wins / games_played) * 100, 0)
        q3_pct = round((q3_wins / games_played) * 100, 0)
        q4_pct = round((q4_wins / games_played) * 100, 0)
        win_pct = round((wins / games_played) * 100, 0)
        
        return {
            "games_played": games_played,
            "win_pct": win_pct,
            "q1": {"quarter_wins": q1_wins, "pct": q1_pct},
            "q2": {"quarter_wins": q2_wins, "pct": q2_pct},
            "q3": {"quarter_wins": q3_wins, "pct": q3_pct},
            "q4": {"quarter_wins": q4_wins, "pct": q4_pct},
        }    

    def debug_output(self, debug:bool, teamId:int, homeTeamId:int, homeTeam:str, awayTeamId:int, awayTeam:str, q1,q2,q3,q4):
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
