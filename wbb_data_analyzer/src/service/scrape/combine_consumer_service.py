import os
import sys
from src.logging.app_logger import AppLogger
from src.service.file_service import FileService

class CombineConsumerService(object):
    def __init__(self, config, team_ids):
        self.logger = AppLogger.get_logger()
        self.config = config
        
        self.team_ids = team_ids

        self.output_dir = config.get("output.data.dir")

        self.boxscore_data_file = config.get("boxscore.data.file")
        self.boxscore_data_dir = config.get("boxscore.data.dir")

        self.playbyplay_data_file = config.get("playbyplay.data.file")
        self.playbyplay_data_dir = config.get("playbyplay.data.dir")

        self.combined_data_file = config.get("combined.data.file")
        self.combined_data_dir = config.get("combined.data.dir")
        #self.combined_data_path = os.path.join(self.output_dir, self.combined_data_dir)
        #os.makedirs(self.combined_data_path, exist_ok=True)

    def combine(self):
        for teamId in self.team_ids:
            combined_data_file_path = os.path.join(self.output_dir, str(teamId), self.combined_data_dir)
            os.makedirs(combined_data_file_path, exist_ok=True)

            boxscore_file_path = os.path.join(self.output_dir, str(teamId), self.boxscore_data_dir)
            boxscores = FileService.read_all_files_in_directory(boxscore_file_path)

            playbyplay_file_path = os.path.join(self.output_dir, str(teamId), self.playbyplay_data_dir)
            playbyplays = FileService.read_all_files_in_directory(playbyplay_file_path)

            for boxscore in boxscores:
                season = boxscore["season"]
                playbyplay = (list(filter(lambda pbp: pbp["gameId"] == boxscore["gameId"], playbyplays)))[0]
                combined = self.build_object(boxscore, playbyplay)
                
                data_file_path = os.path.join(combined_data_file_path, self.combined_data_file.replace("YYYY", str(season)))
                FileService.append(data_file_path, combined)

    def build_object(self, boxscore, playbyplay) -> dict:
        season = boxscore["season"]
        winningTeamId = boxscore["winningTeamId"]
        losingTeamId = boxscore["losingTeamId"]
        homeTeamId = boxscore["homeTeamId"]
        awayTeamId = boxscore["awayTeamId"]

        combined = {
            "season": season,
            "gameId": boxscore["gameId"],
            "game_date": boxscore["game_date"],
            "homeTeamId": homeTeamId,
            "awayTeamId": awayTeamId,
            "winningTeamId": winningTeamId,
            "losingTeamId": losingTeamId,
            "homeTeam":  playbyplay["homeTeam"],
            "awayTeam": playbyplay["awayTeam"],
            "outcome": {
                "winningTeam": boxscore["winningTeam"]["team"],
                "winnningTeamId": boxscore["winningTeam"]["teamId"],
                "winningTeamPoints": boxscore["winningTeam"]["PTS"],
                "winningTeamMargin": boxscore["winningTeam"]["margin"],

                "losingTeam": boxscore["losingTeam"]["team"],
                "losningTeamId": boxscore["losingTeam"]["teamId"],
                "losingTeamPoints": boxscore["losingTeam"]["PTS"],
                "losingTeamMargin": boxscore["losingTeam"]["margin"],

                "end_quarter_scores": {
                        "q1": {
                        "q1_home_team_score": playbyplay["end_quarter_scores"]["q1"]["q1_home_team_score"],
                        "q1_away_team_score": playbyplay["end_quarter_scores"]["q1"]["q1_away_team_score"],

                        "q1_winning_team_score": playbyplay["end_quarter_scores"]["q1"]["q1_home_team_score"] if winningTeamId == homeTeamId else playbyplay["end_quarter_scores"]["q1"]["q1_away_team_score"],
                        "q1_losing_team_score": playbyplay["end_quarter_scores"]["q1"]["q1_home_team_score"] if winningTeamId == awayTeamId else playbyplay["end_quarter_scores"]["q1"]["q1_away_team_score"],
                        },
                        "q2": {
                        "q2_home_team_score": playbyplay["end_quarter_scores"]["q2"]["q2_home_team_score"],
                        "q2_away_team_score": playbyplay["end_quarter_scores"]["q2"]["q2_away_team_score"],

                        "q2_winning_team_score": playbyplay["end_quarter_scores"]["q2"]["q2_home_team_score"] if winningTeamId == homeTeamId else playbyplay["end_quarter_scores"]["q2"]["q2_away_team_score"],
                        "q2_losing_team_score": playbyplay["end_quarter_scores"]["q2"]["q2_home_team_score"] if winningTeamId == awayTeamId else playbyplay["end_quarter_scores"]["q2"]["q2_away_team_score"],
                        },
                        "q3": {
                        "q3_home_team_score": playbyplay["end_quarter_scores"]["q3"]["q3_home_team_score"],
                        "q3_away_team_score": playbyplay["end_quarter_scores"]["q3"]["q3_away_team_score"],

                        "q3_winning_team_score": playbyplay["end_quarter_scores"]["q3"]["q3_home_team_score"] if winningTeamId == homeTeamId else playbyplay["end_quarter_scores"]["q3"]["q3_away_team_score"],
                        "q3_losing_team_score": playbyplay["end_quarter_scores"]["q3"]["q3_home_team_score"] if winningTeamId == awayTeamId else playbyplay["end_quarter_scores"]["q3"]["q3_away_team_score"],
                        },
                        "q4": {
                        "q4_home_team_score": playbyplay["end_quarter_scores"]["q4"]["q4_home_team_score"],
                        "q4_away_team_score": playbyplay["end_quarter_scores"]["q4"]["q4_away_team_score"],

                        "q4_winning_team_score": playbyplay["end_quarter_scores"]["q4"]["q4_home_team_score"] if winningTeamId == homeTeamId else playbyplay["end_quarter_scores"]["q4"]["q4_away_team_score"],
                        "q4_losing_team_score": playbyplay["end_quarter_scores"]["q4"]["q4_home_team_score"] if winningTeamId == awayTeamId else playbyplay["end_quarter_scores"]["q4"]["q4_away_team_score"],
                        },
                } if playbyplay["available"] == "Y" else {},
            },
            "winningTeamStats": {
                "teamId": winningTeamId,
                "PTS": playbyplay["homeTeamPoints"] if winningTeamId == homeTeamId else playbyplay["awayTeamPoints"],
                "FG": boxscore["homeTeam"]["FG"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["FG"],
                "FGA": boxscore["homeTeam"]["FGA"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["FGA"],
                "FG3": boxscore["homeTeam"]["FG3"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["FG3"],
                "FG3A": boxscore["homeTeam"]["FG3A"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["FG3A"],
                "FT": boxscore["homeTeam"]["FT"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["FT"],
                "FTA": boxscore["homeTeam"]["FTA"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["FTA"],
                "REB": boxscore["homeTeam"]["REB"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["REB"],
                "DREB": boxscore["homeTeam"]["DREB"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["DREB"],
                "OREB": boxscore["homeTeam"]["OREB"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["OREB"],
                "AST": boxscore["homeTeam"]["AST"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["AST"],
                "TO": boxscore["homeTeam"]["TO"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["TO"],
                "STL": boxscore["homeTeam"]["STL"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["STL"],
                "BLK": boxscore["homeTeam"]["BLK"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["BLK"],
                "PF": boxscore["homeTeam"]["PF"] if winningTeamId == homeTeamId else boxscore["awayTeam"]["PF"],
            },
            "losingTeamStats": {
                "teamId": losingTeamId,
                "PTS": playbyplay["homeTeamPoints"] if winningTeamId == awayTeamId else playbyplay["awayTeamPoints"],
                "FG": boxscore["homeTeam"]["FG"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["FG"],
                "FGA": boxscore["homeTeam"]["FGA"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["FGA"],
                "FG3": boxscore["homeTeam"]["FG3"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["FG3"],
                "FG3A": boxscore["homeTeam"]["FG3A"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["FG3A"],
                "FT": boxscore["homeTeam"]["FT"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["FT"],
                "FTA": boxscore["homeTeam"]["FTA"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["FTA"],
                "REB": boxscore["homeTeam"]["REB"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["REB"],
                "DREB": boxscore["homeTeam"]["DREB"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["DREB"],
                "OREB": boxscore["homeTeam"]["OREB"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["OREB"],
                "AST": boxscore["homeTeam"]["AST"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["AST"],
                "TO": boxscore["homeTeam"]["TO"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["TO"],
                "STL": boxscore["homeTeam"]["STL"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["STL"],
                "BLK": boxscore["homeTeam"]["BLK"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["BLK"],
                "PF": boxscore["homeTeam"]["PF"] if winningTeamId == awayTeamId else boxscore["awayTeam"]["PF"],
            },
            "boxscore_url": boxscore["boxscore_url"],
            "boxscore_file": boxscore["boxscore_file"],
            "playbyplay_url": playbyplay["playbyplay_url"],
            "playbyplay_file": playbyplay["playbyplay_file"]
        }

        return combined
