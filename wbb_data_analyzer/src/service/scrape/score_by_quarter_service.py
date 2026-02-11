import json
import re
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService
from src.service.utility_service import UtilityService

class ScoreByQuarterService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.config = config

        self.output_dir = UtilityService.get_output_dir()
        self.scrape_data_dir = UtilityService.get_scrape_data_dir()
        self.metadata_file = UtilityService.get_metadata_file()

        self.seasons = UtilityService.get_seasons()
        self.team_ids = UtilityService.get_team_ids()

        self.boxscore_data_file = UtilityService.get_boxscore_data_file()
        self.boxscore_data_dir = UtilityService.get_boxscore_data_dir()

        self.playbyplay_data_file = UtilityService.get_playbyplay_data_file()
        self.playbyplay_data_dir = UtilityService.get_playbyplay_data_dir()

    def get_quarter_scores(self, game:dict, soup, label:str):
        #self.logger.info(str(game))
        homeTeam, awayTeam = self.get_team_data(soup, game, label)

        if homeTeam is None or awayTeam is None:
            self.logger.info(label + "cannot get quarter scores")
            return None, None
        
        # self.logger.info(str(homeTeam))
        # self.logger.info(str(awayTeam))

        homeTeamQuarterScores = [int(item["displayValue"]) for item in homeTeam["calculatedLinescores"]]
        awayTeamQuarterScores = [int(item["displayValue"]) for item in awayTeam["calculatedLinescores"]]

        # self.logger.info(str(homeTeamQuarterScores))
        # self.logger.info(str(awayTeamQuarterScores))

        homeTeamQtrs = {
            "1": homeTeamQuarterScores[0], 
            "2": homeTeamQuarterScores[1], 
            "3": homeTeamQuarterScores[2], 
            "4": homeTeamQuarterScores[3]
        }

        awayTeamQtrs = {
            "1": awayTeamQuarterScores[0], 
            "2": awayTeamQuarterScores[1], 
            "3": awayTeamQuarterScores[2], 
            "4": awayTeamQuarterScores[3]
        }

        quarter_scores = {
            "q1": {"q1_home_team_score": homeTeamQtrs["1"], "q1_away_team_score": awayTeamQtrs["1"]},
            "q2": {"q2_home_team_score": homeTeamQtrs["2"], "q2_away_team_score": awayTeamQtrs["2"]},
            "q3": {"q3_home_team_score": homeTeamQtrs["3"], "q3_away_team_score": awayTeamQtrs["3"]},
            "q4": {"q4_home_team_score": homeTeamQtrs["4"], "q4_away_team_score": awayTeamQtrs["4"]},
        }

        homeTeamCumulative = {
            "1": homeTeamQuarterScores[0], 
            "2": homeTeamQuarterScores[0] + homeTeamQuarterScores[1], 
            "3": homeTeamQuarterScores[0] + homeTeamQuarterScores[1] + homeTeamQuarterScores[2], 
            "4": homeTeamQuarterScores[0] + homeTeamQuarterScores[1] + homeTeamQuarterScores[2] + homeTeamQuarterScores[3]
        }

        awayTeamCumulative = {
            "1": awayTeamQuarterScores[0], 
            "2": awayTeamQuarterScores[0] + awayTeamQuarterScores[1], 
            "3": awayTeamQuarterScores[0] + awayTeamQuarterScores[1] + awayTeamQuarterScores[2], 
            "4": awayTeamQuarterScores[0] + awayTeamQuarterScores[1] + awayTeamQuarterScores[2] + awayTeamQuarterScores[3]
        }

        end_quarter_scores = {
            "q1": {"q1_home_team_score": homeTeamCumulative["1"], "q1_away_team_score": awayTeamCumulative["1"]},
            "q2": {"q2_home_team_score": homeTeamCumulative["2"], "q2_away_team_score": awayTeamCumulative["2"]},
            "q3": {"q3_home_team_score": homeTeamCumulative["3"], "q3_away_team_score": awayTeamCumulative["3"]},
            "q4": {"q4_home_team_score": homeTeamCumulative["4"], "q4_away_team_score": awayTeamCumulative["4"]},
        }

        # self.logger.info(str(homeTeamCumulative))
        # self.logger.info(str(awayTeamCumulative))
        # self.logger.info(str(end_quarter_scores))

        return quarter_scores, end_quarter_scores
        
    def get_team_data(self, soup, game, label):
        for script in soup.find_all("script"):
            text = script.get_text(strip=True)

            if '"tms":[' in text:
                try:
                    start_position = text.find('"tms":[')
                    #self.logger.info("start_position for tms: " + str(start_position))
                    if start_position == -1:
                        self.logger.error(label + "cannot locate tms.  No data available is assumed.")
                        return None, None
                    
                    #self.logger.info(text[start_position:start_position+3000])
                                        
                    # find all occurrences of '{"id":'
                    tms_string = text[start_position:start_position+3000]
                    sub = '{"id":'
                    indices = []
                    start = 0

                    while True:
                        index = tms_string.find(sub, start)
                        if index == -1:
                            break
                        indices.append(index)
                        start = index+1

                    #self.logger.info(str(indices))
                    if len(indices) == 0 or len(indices) != 2:
                        self.logger.info(label + "wrong indices values")
                        return None, None
                    
                    tm1_ix = indices[0]
                    tm2_ix = indices[1]

                    tm1 = tms_string[tm1_ix:tm2_ix-1]
                    #self.logger.info(str(tm1))

                    tm2 = tms_string[tm2_ix:]
                    #self.logger.info(str(tm2))

                    tm2_end_ix = tms_string.rfind('}],') 
                    if tm2_end_ix == -1:
                        self.logger.info("cannot locate endstring")
                        return None, None
                    
                    tm2 = tms_string[tm2_ix:tm2_end_ix+1]
                    #self.logger.info(str(tm2))

                    team1 = json.loads(tm1)
                    #self.logger.info(str(team1))

                    team2 = json.loads(tm2)
                    #self.logger.info(str(team2))

                    if team1["id"] == game["homeTeamId"]:
                        return team1, team2
                    else:
                        return team2, team1
                    
                except Exception as e:
                    self.logger.error(label + str(e))
                    return None, None
                
        return None, None


    def process_playbyplay_file_version1(self, playbyplay_file:str, label):
        #self.logger.info(playbyplay_file)
        with open(playbyplay_file, "r", encoding="utf8") as file:
            soup = BeautifulSoup(file, "html.parser")

            for script in soup.find_all("script"):
                text = script.get_text(strip=True)

                if 'playGrps' in text:
                    try:
                        start_position = text.find("playGrps")
                        if start_position == -1:
                            self.logger.error(label + "cannot locate playGrps.  No data available is assumed.")
                            return None
                        
                        end_position = text.find("]]", start_position)
                        if end_position == -1:
                            self.logger.error(label + "cannot find end_position. No data available is assumed.")
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
        

    def process_playbyplay_file_version2(self, playbyplay_file:str, label):
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
                            self.logger.error(label + "cannot locate plays.  No data available is assumed.")
                            return None
                        
                        #self.logger.info(str(text[start_position:start_position+40]))
                        end_position = text.find("}}]", start_position)
                        #self.logger.info("end_position for plays: " + str(end_position))
                        if end_position == -1:
                            self.logger.error(label + "cannot find end_position.  No data available is assumed.")
                            return None
                        
                        pbp_data = text[start_position:end_position+3]
                        #self.logger.info(str(pbp_data))
                        pbp_data = pbp_data.replace('"plays":', '')  
                        pbp_array = json.loads(pbp_data)

                        for p in pbp_array:
                            #self.logger.info(str(p))
                            #self.logger.info(str(p["type"]))
                            if "type" in p and "categoryId" in p["type"]:
                                #self.logger.info(str(p))
                                if p["type"]["categoryId"] == "1017" or p["type"]["categoryId"] == "1018" or p["type"]["categoryId"] == "1019":
                                    #self.logger.info(str(p))
                                    #self.logger.info(str(p["period"]) + " " + str(p["type"]) + " " + str(p["title"]))
                                    #self.logger.info("away score: " + str(p["awScr"]) + " home score: " + str(p["hmScr"]))
                                    #self.logger.info(str(p["period"]))
                                    #self.logger.info("away score: " + str(p["awScr"]) + " home score: " + str(p["hmScr"]))
                                    #self.logger.info(str(p["awScr"]))
                                    #self.logger.info(str(p["hmScr"]))
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