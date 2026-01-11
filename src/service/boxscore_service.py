import os
from bs4 import BeautifulSoup
from src.logging.app_logger import AppLogger
from src.service.file_service import FileService

class BoxscoreService(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.config = config
        self.output_dir = config.get("output.data.dir")
        metadata_file = config.get("metadata.file")
        self.metadata_file_path = os.path.join(self.output_dir, metadata_file)
        self.seasons = [season.strip() for season in config.get("seasons").split(",")]

        self.boxscore_data_file = config.get("boxscore.data.file")
        self.boxscore_data_path = os.path.join(self.output_dir, "boxscore")
        os.makedirs(self.boxscore_data_path, exist_ok=True)

    def collect_boxscore_data(self):
        do_boxscore = self.config.get("do.boxscore")
        if not do_boxscore or do_boxscore.strip().lower() != "y":
            self.logger.info("not re-generating box score files")
            return
        
        FileService.delete_all_files_in_directory(self.boxscore_data_path)
        
        games_list = FileService.read_file(self.metadata_file_path)
        for game in games_list:
            boxscore_file = game["boxscore_file"]
            homeTeam, awayTeam, team_totals = self.process_boxscore_file(boxscore_file)
            if team_totals is None:
                self.logger.error("no team totals, returning")
                break

            for t in team_totals:
                if t["team"] == homeTeam:
                    game["homeTeam"] = t
                elif t["team"] == awayTeam:
                    game["away_team"] = t

            # for k,v in game.items():
            #     self.logger.info(k + " -> " + str(v))

            season = game["season"]
            boxscore_data_file_path = os.path.join(self.boxscore_data_path, self.boxscore_data_file.replace("YYYY", str(season)))
            FileService.append(boxscore_data_file_path, game)

    def process_boxscore_file(self, boxscore_file:str):
        with open(boxscore_file, "r", encoding="utf8") as file:
            soup = BeautifulSoup(file, "html.parser")
            #self.logger.info(str(soup))

            # extract home/away team
            homeTeam, awayTeam = self.extract_home_away(soup)

            # extract team stats
            teams = soup.select("div.Boxscore.flex.flex-column:has(.Boxscore__Title)")

            results = []
            for team in teams:
                #results.append(self.extract_team_totals(team))
                team_totals = self.extract_team_totals(team)
                if team_totals is None:
                    self.logger.info(team + ": no totals")
                    return None
                else:
                    #self.logger.info(str(team_totals))
                    results.append(team_totals)
                    #return team_totals

            return homeTeam, awayTeam, results
        
    def extract_home_away(self, soup):
        homeTeam, awayTeam = None, None
        for script in soup.find_all("script"):
            text = script.get_text(strip=True)
            if 'prsdTms' in text:
                try:
                    position = text.find("prsdTms")
                    if position == -1:
                        self.logger.error("cannot locate prsdTms")
                        return None, None
                    
                    prsdTms = text[position:position + 2000]

                    home = prsdTms[0:200].replace('"', "").replace("{ home: ", "").replace("{", "").replace("}", "") #.replace(" ", "")
                    # home_tokens = [t.strip() for t in home.split(",") if "UNC" in t]
                    home_tokens = [t.strip() for t in home.split(",") if "displayName" in t]
                    homeTeam = (home_tokens[0].split(":"))[1]
                    #self.logger.info(homeTeam)

                    #self.logger.info(prsdTms)
                    position = prsdTms.find("away")
                    if position == -1:
                        self.logger.error("cannot locate away")
                        return None, None
                    
                    away = prsdTms[position:position + 2000].replace('"', "").replace("{ away: ", "").replace("{", "").replace("}", "")
                    away_tokens = [t.strip() for t in away.split(",") if "displayName" in t]
                    awayTeam = (away_tokens[0].split(":"))[1]
                    #self.logger.info(awayTeam)

                    return homeTeam, awayTeam
                except Exception as e:
                    self.logger.error(f"JSON extraction failed: {e}")
                    
        return None, None



    def extract_team_totals(self, team_block):
        team_name = team_block.select_one(".BoxscoreItem__TeamName").get_text(strip=True)
        
        scroller = team_block.select_one("div.Table__Scroller table")
        if not scroller:
            return None
        
        all_rows = scroller.select("tbody tr")
        if len(all_rows) < 10:  # Basic sanity check
            return None
        
        # Team totals are 2nd-to-last row (index -2)
        totals_row = all_rows[-2]
        cells = [td.get_text(strip=True) for td in totals_row.select("td")]
        
        # Just verify it has the expected structure (empty first cell, PTS in second)
        if len(cells) >= 13 and not cells[0] and cells[1] and cells[1].isdigit():
            stats = cells[1:]
            return_stats = dict()
            return_stats["team"] = team_name
            
            return_stats["PTS"] = int(stats[0])

            fg_stats = stats[1].split("-")
            fgm = fg_stats[0]
            fga = fg_stats[1]
            return_stats["FG"] = int(fgm)
            return_stats["FGA"] = int(fga)

            fg3_stats = stats[2].split("-")
            fg3m = fg3_stats[0]
            fg3a = fg3_stats[1]
            return_stats["FG3"] = int(fg3m)
            return_stats["FG3A"] = int(fg3a)

            ft_stats = stats[3].split("-")
            ftm = ft_stats[0]
            fta = ft_stats[1]
            return_stats["FT"] = int(ftm)
            return_stats["FTA"] = int(fta)

            return_stats["REB"] = int(stats[4])
            return_stats["AST"] = int(stats[5])
            return_stats["TO"] = int(stats[6])
            return_stats["STL"] = int(stats[7])
            return_stats["BLK"] = int(stats[8])
            return_stats["OREB"] = int(stats[9])
            return_stats["DREB"] = int(stats[10])
            return_stats["PF"] = int(stats[11])

            return return_stats
        
        return None



        
  