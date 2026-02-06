import json
import re
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class PlaybyplayConsumerService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.config = config

        self.output_dir = config.get("output.data.dir")
        metadata_file = config.get("metadata.file")
        self.metadata_file_path = os.path.join(self.output_dir, metadata_file)

        self.seasons = [season.strip() for season in config.get("seasons").split(",")]
        self.team_id = config.get("team.id")

        # use the box score data to get home/away teams
        self.boxscore_data_file = config.get("boxscore.data.file")
        self.boxscore_data_path = os.path.join(self.output_dir, "boxscore")
        self.boxscore_data = FileService.read_all_files_in_directory(self.boxscore_data_path)

        self.playbyplay_data_file = config.get("playbyplay.data.file")
        self.playbyplay_data_path = os.path.join(self.output_dir, "playbyplay")
        os.makedirs(self.playbyplay_data_path, exist_ok=True)

    def collect_playbyplay_data(self):
        do_playbyplay = self.config.get("do.playbyplay")
        if not do_playbyplay or do_playbyplay.strip().lower() != "y":
            self.logger.info("not re-generating play-by-play files")
            return
        
        FileService.delete_all_files_in_directory(self.playbyplay_data_path)
        
        games_list = FileService.read_file(self.metadata_file_path)
        for game in games_list:
            season = game["season"]
            playbyplay_data_file_path = os.path.join(self.playbyplay_data_path, self.playbyplay_data_file.replace("YYYY", str(season)))

            del game["boxscore_url"] # don't want in playbyplay file
            del game["boxscore_file"] # don't want in playbyplay file

            #self.logger.info(str(game))
            
            boxscore = (list(filter(lambda x: x["game_date"] == game["game_date"], self.boxscore_data)))[0]
            #self.logger.info(str(boxscore))
            if len(boxscore) == 0:
                self.logger.error("uh oh no boxscore")
                continue

            try:
                game["homeTeamId"] = boxscore["homeTeamId"]
                game["awayTeamId"] = boxscore["awayTeamId"]
                game["homeTeam"] = boxscore["homeTeam"]["team"]
                game["awayTeam"] = boxscore["awayTeam"]["team"]
                game["homeTeamPoints"] = boxscore["homeTeam"]["PTS"]
                game["awayTeamPoints"] = boxscore["awayTeam"]["PTS"]

                playbyplay_file = game["playbyplay_file"]
                playbyplay_data = self.process_playbyplay_file_version1(playbyplay_file)

                # if playbyplay_data is None:
                #     playbyplay_file = game["playbyplay_file"]
                #     playbyplay_data = self.process_playbyplay_file_version2(playbyplay_file)
                   

                # if playbyplay_data is None:
                #     game["available"] = "N"
                #     FileService.append(playbyplay_data_file_path, game)
                #     continue

                if playbyplay_data is not None:
                    game["available"] = "Y"
                    q1 = playbyplay_data[0]
                    q2 = playbyplay_data[1]
                    q3 = playbyplay_data[2]
                    q4 = playbyplay_data[3]

                    q1_home_team_score = q1[len(q1)-1]["homeScore"]
                    q1_away_team_score = q1[len(q1)-1]["awayScore"]

                    q2_home_team_score = q2[len(q2)-1]["homeScore"]
                    q2_away_team_score = q2[len(q2)-1]["awayScore"]

                    q3_home_team_score = q3[len(q3)-1]["homeScore"]
                    q3_away_team_score = q3[len(q3)-1]["awayScore"]

                    q4_home_team_score = q4[len(q4)-1]["homeScore"]
                    q4_away_team_score = q4[len(q4)-1]["awayScore"]

                    game["end_quarter_scores"] = {
                        "q1": {"q1_home_team_score": q1_home_team_score, "q1_away_team_score": q1_away_team_score},
                        "q2": {"q2_home_team_score": q2_home_team_score, "q2_away_team_score": q2_away_team_score},
                        "q3": {"q3_home_team_score": q3_home_team_score, "q3_away_team_score": q3_away_team_score},
                        "q4": {"q4_home_team_score": q4_home_team_score, "q4_away_team_score": q4_away_team_score},
                    }

                    FileService.append(playbyplay_data_file_path, game)
                    continue

                # try version 2 of the scrape file
                playbyplay_file = game["playbyplay_file"]
                playbyplay_dict = self.process_playbyplay_file_version2(playbyplay_file)
                if playbyplay_dict is not None:
                    for k,v in playbyplay_dict.items():
                        self.logger.info(str(k) + " -> " + str(v))

                    game["end_quarter_scores"] = {
                        "q1": {"q1_home_team_score": playbyplay_dict["1"]["homeScore"], "q1_away_team_score": playbyplay_dict["1"]["awayScore"]},
                        "q2": {"q2_home_team_score": playbyplay_dict["2"]["homeScore"], "q2_away_team_score": playbyplay_dict["2"]["awayScore"]},
                        "q3": {"q3_home_team_score": playbyplay_dict["3"]["homeScore"], "q3_away_team_score": playbyplay_dict["3"]["awayScore"]},
                        "q4": {"q4_home_team_score": playbyplay_dict["4"]["homeScore"], "q4_away_team_score": playbyplay_dict["4"]["awayScore"]}
                    }
                    FileService.append(playbyplay_data_file_path, game)
                    continue
            
                game["available"] = "N"
                FileService.append(playbyplay_data_file_path, game)

            except Exception as e:
                self.logger.info("uh oh, no playbyplay")
                self.logger.info(str(e))

    def process_playbyplay_file_version1(self, playbyplay_file:str):
        #self.logger.info(playbyplay_file)
        with open(playbyplay_file, "r", encoding="utf8") as file:
            soup = BeautifulSoup(file, "html.parser")

            for script in soup.find_all("script"):
                text = script.get_text(strip=True)

                if 'playGrps' in text:
                    try:
                        start_position = text.find("playGrps")
                        if start_position == -1:
                            self.logger.error("cannot locate playGrps")
                            return None
                        
                        end_position = text.find("]]", start_position)
                        if end_position == -1:
                            self.logger.error("cannot find end_position")
                            return None
                        
                        pbp_data = text[start_position:end_position+2]
                        pbp_data = pbp_data.replace('playGrps":', '')  
                        pbp_array = json.loads(pbp_data)

                        # for quarter_array in pbp_array:
                        #     for play in quarter_array:
                        #         self.logger.info(str(play))
                    except Exception as e:
                        #self.logger.error(str(e))
                        return None

                    return pbp_array
                
        return None
        

    def process_playbyplay_file_version2(self, playbyplay_file:str):
        #self.logger.info(playbyplay_file)
        return_dict = dict()

        with open(playbyplay_file, "r", encoding="utf8") as file:
            soup = BeautifulSoup(file, "html.parser")

            for script in soup.find_all("script"):
                text = script.get_text(strip=True)

                if '"plays":[' in text:
                    try:
                        start_position = text.find('"plays":[')
                        #self.logger.info("start_position for plays: " + str(start_position))
                        if start_position == -1:
                            self.logger.error("cannot locate plays")
                            return None
                        
                        #self.logger.info(str(text[start_position:start_position+40]))
                        end_position = text.find("}}]", start_position)
                        #self.logger.info("end_position for plays: " + str(end_position))
                        if end_position == -1:
                            self.logger.error("cannot find end_position")
                            return None
                        
                        pbp_data = text[start_position:end_position+3]
                        #self.logger.info(str(pbp_data))
                        pbp_data = pbp_data.replace('"plays":', '')  
                        pbp_array = json.loads(pbp_data)
                        for p in pbp_array:
                            if p["type"]["categoryId"] == "1017" or p["type"]["categoryId"] == "1018":
                                #self.logger.info(str(p))
                                #self.logger.info(str(p["period"]) + " " + str(p["type"]) + " " + str(p["title"]))
                                #self.logger.info("away score: " + str(p["awScr"]) + " home score: " + str(p["hmScr"]))
                                #self.logger.info(str(p["period"]))
                                #self.logger.info("away score: " + str(p["awScr"]) + " home score: " + str(p["hmScr"]))
                                return_dict[str(p["period"]["number"])] = {"awayScore": p["awScr"], "homeScore": p["hmScr"]}
                                #self.logger.info(str(return_dict))

                        # for quarter_array in pbp_array:
                        #     for play in quarter_array:
                        #         self.logger.info(str(play))
                    except Exception as e:
                        self.logger.error(str(e))
                        return None

                    #return pbp_array
                    # for k,v in return_dict.items():
                    #     self.logger.info(k + " -> " + str(v))
                    return return_dict
                
        return None