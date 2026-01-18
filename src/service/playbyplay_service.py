import json
import re
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class PlaybyplayService(object):
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
                sys.exit()

            game["homeTeamId"] = boxscore["homeTeamId"]
            game["awayTeamId"] = boxscore["awayTeamId"]
            game["homeTeam"] = boxscore["homeTeam"]["team"]
            game["awayTeam"] = boxscore["awayTeam"]["team"]
            game["homeTeamPoints"] = boxscore["homeTeam"]["PTS"]
            game["awayTeamPoints"] = boxscore["awayTeam"]["PTS"]

            playbyplay_file = game["playbyplay_file"]
            playbyplay_data = self.process_playbyplay_file(playbyplay_file)

            if playbyplay_data is None:
                game["available"] = "N"
                FileService.append(playbyplay_data_file_path, game)
                continue

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

            #game["playbyplay"] = playbyplay_data # too much data for a season file

            FileService.append(playbyplay_data_file_path, game)

    def process_playbyplay_file(self, playbyplay_file:str):
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
                        self.logger.error(str(e))
                        return None

                    return pbp_array
                
        return None
        
        
    # def extract_home_away(self, soup):
    #     homeTeam, awayTeam = None, None
    #     homeTeamId, awayTeamId = None, None
    #     for script in soup.find_all("script"):
    #         text = script.get_text(strip=True)
    #         if 'prsdTms' in text:
    #             try:
    #                 position = text.find("prsdTms")
    #                 if position == -1:
    #                     self.logger.error("cannot locate prsdTms")
    #                     return None
                    
    #                 prsdTms = text[position:position + 2000]

    #                 home = prsdTms[0:200].replace('"', "").replace("{ home: ", "").replace("{", "").replace("}", "") #.replace(" ", "")
    #                 home_tokens = [t.strip() for t in home.split(",") if "displayName" in t]
    #                 homeTeam = (home_tokens[0].split(":"))[1]
    #                 #self.logger.info(homeTeam)

    #                 #self.logger.info(str(home))
    #                 home = home.replace("prsdTms:home:", "")
    #                 home = home.replace("prsdTms:  ", "")
    #                 home_tokens = [t.strip() for t in home.split(",")]
    #                 #self.logger.info(str(home_tokens))
    #                 homeTeamId = (home_tokens[0].split(":"))[1]
    #                 #self.logger.info(str(homeTeamId))

    #                 #self.logger.info(prsdTms)
    #                 position = prsdTms.find("away")
    #                 if position == -1:
    #                     self.logger.error("cannot locate away")
    #                     return None
                    
    #                 away = prsdTms[position:position + 2000].replace('"', "").replace("{ away: ", "").replace("{", "").replace("}", "")
    #                 away_tokens = [t.strip() for t in away.split(",") if "displayName" in t]
    #                 awayTeam = (away_tokens[0].split(":"))[1]
                    
    #                 away = away.replace("away:", "")
    #                 away_tokens = [t.strip() for t in away.split(",")]
    #                 awayTeamId = (away_tokens[0].split(":"))[1]

    #                 return {
    #                     "homeTeam": homeTeam,
    #                     "awayTeam": awayTeam,
    #                     "homeTeamId": homeTeamId,
    #                     "awayTeamId": awayTeamId
    #                 }
    #             except Exception as e:
    #                 self.logger.error(f"JSON extraction failed: {e}")
                    
    #     return None



    # def extract_team_totals(self, team_block):
    #     team_name = team_block.select_one(".BoxscoreItem__TeamName").get_text(strip=True)
    #     #self.logger.info(team_name)
        
    #     scroller = team_block.select_one("div.Table__Scroller table")
    #     if not scroller:
    #         self.logger.info("no scroller")
    #         return None
        
    #     all_rows = scroller.select("tbody tr")
    #     if len(all_rows) < 10:  # Basic sanity check
    #         self.logger.info("not at least 10 rows")
    #         return None
        
    #     # Team totals are 2nd-to-last row (index -2)
    #     totals_row = all_rows[-2]
    #     cells = [td.get_text(strip=True) for td in totals_row.select("td")]

    #     #self.logger.info(str(cells))
        
    #     # Just verify it has the expected structure (empty first cell, PTS in second)
    #     if len(cells) >= 13 and not cells[0] and cells[1] and cells[1].isdigit():
    #         stats = cells[1:]
    #         #self.logger.info(str(stats))
    #         return_stats = dict()
    #         return_stats["team"] = team_name
            
    #         return_stats["PTS"] = int(stats[0])

    #         fg_stats = stats[1].split("-")
    #         fgm = fg_stats[0]
    #         fga = fg_stats[1]
    #         return_stats["FG"] = int(fgm)
    #         return_stats["FGA"] = int(fga)

    #         fg3_stats = stats[2].split("-")
    #         fg3m = fg3_stats[0]
    #         fg3a = fg3_stats[1]
    #         return_stats["FG3"] = int(fg3m)
    #         return_stats["FG3A"] = int(fg3a)

    #         ft_stats = stats[3].split("-")
    #         ftm = ft_stats[0]
    #         fta = ft_stats[1]
    #         return_stats["FT"] = int(ftm)
    #         return_stats["FTA"] = int(fta)

    #         return_stats["REB"] = int(stats[4])
    #         return_stats["AST"] = int(stats[5])
    #         return_stats["TO"] = int(stats[6])
    #         return_stats["STL"] = int(stats[7])
    #         return_stats["BLK"] = int(stats[8])
    #         return_stats["OREB"] = int(stats[9])
    #         return_stats["DREB"] = int(stats[10])
    #         return_stats["PF"] = int(stats[11])

    #         #self.logger.info(str(return_stats))

    #         return return_stats
    #     else:
    #         self.logger.info("no data")
        
    #     return None



        
  