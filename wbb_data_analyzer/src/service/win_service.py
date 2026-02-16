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
        self.team_ids = UtilityService.get_team_ids()

        self.duke_team_id = UtilityService.get_duke_team_id()
        self.unc_team_id = UtilityService.get_unc_team_id()

        self.output_dir = UtilityService.get_output_dir()
        self.combined_data_file = UtilityService.get_combined_data_file()
        self.combined_data_dir = UtilityService.get_combined_data_dir()

    def losses(self):
        for teamId in self.team_ids:
            combined_data_path = os.path.join(self.output_dir, str(teamId), self.combined_data_dir)
            data_list = FileService.read_all_files_in_directory(combined_data_path)

            losses = list()
            for data in data_list:
                losingTeamId = data["losingTeamId"]
                if teamId != losingTeamId:
                    continue

                losses.append({
                        "gameDate": data["game_date"], 
                        "winner": data["outcome"]["winningTeam"],
                        "loser": data["outcome"]["losingTeam"],
                        "winPoints": data["outcome"]["winningTeamPoints"],
                        "winPoints": data["outcome"]["winningTeamPoints"],
                        "lossPoints": data["outcome"]["losingTeamPoints"],
                        "homeOrAway": "home" if data["homeTeamId"] == teamId else "away"
                        })

            for loss in losses:
                self.logger.info(str(loss))


    def head_to_head_scores(self):
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

    def duke_unc(self):
        combined_data_path = os.path.join(self.output_dir, str(self.duke_team_id), self.combined_data_dir)
        data_list = FileService.read_all_files_in_directory(combined_data_path)

        statList = list()

        for data in data_list:
            stats = {
                "duke": {"winLoss": "", "homeAway": ""},
                "unc": {"winLoss": "", "homeAway": ""},
            }

            winningTeamId = data["winningTeamId"]
            losingTeamId = data["losingTeamId"]
            homeTeamId = data["homeTeamId"]
            awayTeamId = data["awayTeamId"]

            if not (self.unc_team_id == winningTeamId  or  self.unc_team_id == losingTeamId):
                continue

            winningTeamStats = data["winningTeamStats"]
            winningTeamFT = winningTeamStats["FT"]
            winningTeamFTA = winningTeamStats["FTA"]
            winningTeamPF = winningTeamStats["PF"]
            winningTeamAST = winningTeamStats["AST"]
            winningTeamTO = winningTeamStats["TO"]
            winningTeamFG = winningTeamStats["FG"]
            winningTeamFGA = winningTeamStats["FGA"]

            losingTeamStats = data["losingTeamStats"]
            losingTeamFT = losingTeamStats["FT"]
            losingTeamFTA = losingTeamStats["FTA"]
            losingTeamPF = losingTeamStats["PF"]
            losingTeamAST = losingTeamStats["AST"]
            losingTeamTO = losingTeamStats["TO"]
            losingTeamFG = losingTeamStats["FG"]
            losingTeamFGA = losingTeamStats["FGA"]

            if self.duke_team_id == winningTeamId:
                stats["duke"]["winLoss"] = "win"
                stats["unc"]["winLoss"] = "loss"

                stats["duke"]["FT"] = winningTeamFT
                stats["duke"]["FTA"] = winningTeamFTA
                stats["duke"]["PF"] = winningTeamPF
                stats["duke"]["AST"] = winningTeamAST
                stats["duke"]["TO"] = winningTeamTO
                stats["duke"]["FG"] = winningTeamFG
                stats["duke"]["FGA"] = winningTeamFGA
                
                stats["unc"]["FT"] = losingTeamFT
                stats["unc"]["FTA"] = losingTeamFTA
                stats["unc"]["PF"] = losingTeamPF
                stats["unc"]["AST"] = losingTeamAST
                stats["unc"]["TO"] = losingTeamTO
                stats["unc"]["FG"] = losingTeamFG
                stats["unc"]["FGA"] = losingTeamFGA
            else:
                stats["duke"]["winLoss"] = "loss"
                stats["unc"]["winLoss"] = "win"

                stats["duke"]["FT"] = losingTeamFT
                stats["duke"]["FTA"] = losingTeamFTA
                stats["duke"]["PF"] = losingTeamPF
                stats["duke"]["AST"] = losingTeamAST
                stats["duke"]["TO"] = losingTeamTO
                stats["duke"]["FG"] = losingTeamFG
                stats["duke"]["FGA"] = losingTeamFGA

                stats["unc"]["FT"] = winningTeamFT
                stats["unc"]["FTA"] = winningTeamFTA
                stats["unc"]["PF"] = winningTeamPF
                stats["unc"]["AST"] = winningTeamAST
                stats["unc"]["TO"] = winningTeamTO
                stats["unc"]["FG"] = winningTeamFG
                stats["unc"]["FGA"] = winningTeamFGA

            if self.duke_team_id == homeTeamId:
                stats["duke"]["homeAway"] = "home"
                stats["unc"]["homeAway"] = "away"
            else:
                stats["duke"]["homeAway"] = "away"
                stats["unc"]["homeAway"] = "home"

            outcome = data["outcome"]["winningTeam"] + " " + str(data["outcome"]["winningTeamPoints"]) + ", " + data["outcome"]["losingTeam"] + " " + str(data["outcome"]["losingTeamPoints"])
            if homeTeamId == self.duke_team_id:
                outcome += " (home game)"
            else:
                outcome += " (away game)"

            ftduke = str(stats["duke"]["FT"]) + "-" + str(stats["duke"]["FTA"])
            pfduke = str(stats["duke"]["PF"])
            ftunc = str(stats["unc"]["FT"]) + "-" + str(stats["unc"]["FTA"])
            pfunc = str(stats["unc"]["PF"])

            ratioduke = str(stats["duke"]["AST"]) + "/" + str(stats["duke"]["TO"]) + " (" + f"{stats["duke"]["AST"] / stats["duke"]["TO"]:.2f}" + ")"
            ratiounc = str(stats["unc"]["AST"]) + "/" + str(stats["unc"]["TO"]) + " (" + f"{stats["unc"]["AST"] / stats["unc"]["TO"]:.2f}" + ")"

            fgduke = str(stats["duke"]["FG"]) + "-" + str(stats["duke"]["FGA"]) + " (" + f"{stats["duke"]["FG"] * 100 / stats["duke"]["FGA"]:.0f}%" + ")"
            fgunc = str(stats["unc"]["FG"]) + "-" + str(stats["unc"]["FGA"]) + " (" + f"{stats["unc"]["FG"] * 100 / stats["unc"]["FGA"]:.0f}%" + ")"

            #if winningTeamId == self.duke_team_id:
            print(data["game_date"] + " " + outcome.replace("North Carolina Tar Heels", "UNC").replace("Duke Blue Devils", "Duke"))
            print(data["game_date"] + " Duke: " + "FT: " + ftduke + " PF: " + pfduke + " AST/TO: " + ratioduke + " " + fgduke)
            print(data["game_date"] + " UNC : " + "FT: " + ftunc + " PF: " + pfunc + " AST/TO: " + ratiounc + " " + fgunc)
            print("")
            #     for k,v in stats["duke"].items():
            #         self.logger.info("duke " + k + " -> " + str(v))
            # print("")
            # for k,v in stats["unc"].items():
            #     self.logger.info("unc " + k + " -> " + str(v))
            # print("")
