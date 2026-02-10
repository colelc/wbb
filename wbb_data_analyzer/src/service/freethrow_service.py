import os
from src.logging.app_logger import AppLogger
from src.service.file_service import FileService
from src.service.utility_service import UtilityService

class FreethrowService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.output_dir = UtilityService.get_output_dir()
        self.combined_data_file = UtilityService.get_combined_data_file()
        self.combined_data_dir = UtilityService.get_combined_data_dir()
        self.team_ids = UtilityService.get_team_ids()

    def analyze_close_game_ft_percentages(self, win_or_loss):
        for teamId in self.team_ids:
            # collect the boxscore data
            #boxscore_list = FileService.read_all_files_in_directory(self.boxscore_data_path)
            combined_file_path = os.path.join(self.output_dir, str(teamId), self.combined_data_dir)
            boxscore_list = FileService.read_all_files_in_directory(combined_file_path)

            filtered_boxscore_list = list()

            if win_or_loss == "L":
                losses = self.get_losses(boxscore_list, teamId)
                if len(losses) > 0:
                    filtered_boxscore_list = self.filter_losses_by_margin(losses, 5, "less")
            else:
                wins = self.get_wins(boxscore_list, teamId)
                if len(wins) > 0:
                    filtered_boxscore_list = self.filter_wins_by_margin(wins, 5, "less")

            self.freethrow_analyis(filtered_boxscore_list, teamId)
    
    def get_losses(self, boxscore_list, teamId):
        return list(filter(lambda x: x["losingTeamId"] == teamId, boxscore_list))
    
    def get_wins(self, boxscore_list, teamId):
        return list(filter(lambda x: x["winningTeamId"] == teamId, boxscore_list))
    
    def filter_losses_by_margin(self, losing_list, margin, moreOrLess):
        if moreOrLess == "more":
            return list(filter(lambda x: abs(x["outcome"]["losingTeamMargin"]) > abs(margin), losing_list))
        else:
            # return list(filter(lambda x: abs(x["losingTeam"]["margin"]) <= abs(margin), losing_list))
            return list(filter(lambda x: abs(x["outcome"]["losingTeamMargin"]) <= abs(margin), losing_list))
    
    def filter_wins_by_margin(self, winning_list, margin, moreOrLess):
        if moreOrLess == "more":
            return list(filter(lambda x: abs(x["outcome"]["winningTeamMargin"]) > abs(margin), winning_list))
        else:
            return list(filter(lambda x: abs(x["outcome"]["winningTeamMargin"]) <= abs(margin), winning_list))

    def freethrow_analyis(self, data_list, teamId):
        for data in data_list:
            print("")
            winningTeam = data["outcome"]["winningTeam"]
            winningTeamPts = data["outcome"]["winningTeamPoints"]
            losingTeam = data["outcome"]["losingTeam"]
            losingTeamPts = data["outcome"]["losingTeamPoints"]
            winningTeamFTs = data["winningTeamStats"]["FT"]
            winningTeamFTAs = data["winningTeamStats"]["FTA"]
            losingTeamFTs = data["losingTeamStats"]["FT"]
            losingTeamFTAs = data["losingTeamStats"]["FTA"]

            print(data["game_date"] + " " + data["awayTeam"] + " at " + data["homeTeam"])
            print(data["game_date"] + " " + winningTeam + " "  + str(winningTeamPts) + " "  + losingTeam + " "  + str(losingTeamPts))
            print(data["game_date"] + " " + winningTeam + " FT-FTA: " + str(winningTeamFTs) + "-" + str(winningTeamFTAs))
            print(data["game_date"] + " " + losingTeam + " FT-FTA: " + str(losingTeamFTs) + "-" + str(losingTeamFTAs))
