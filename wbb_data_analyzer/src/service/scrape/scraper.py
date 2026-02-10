import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService
from src.service.scrape.boxscore_consumer_service import BoxscoreConsumerService
from src.service.scrape.playbyplay_consumer_service import PlaybyplayConsumerService
from src.service.scrape.combine_consumer_service import CombineConsumerService
from src.service.utility_service import UtilityService

class Scraper(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.espn_url = config.get("espn.url")
        self.team_ids = UtilityService.get_team_ids()
        self.season_results_url = config.get("season.results.url")
        self.seasons = UtilityService.get_seasons()

        self.output_dir = UtilityService.get_output_dir()

        self.scrape_data_dir = UtilityService.get_scrape_data_dir()
        self.schedule_data_dir = UtilityService.get_schedule_data_dir()
        self.boxscore_data_dir = UtilityService.get_boxscore_data_dir()
        self.playbyplay_data_dir = UtilityService.get_playbyplay_data_dir()

        self.scrape_schedule_file = UtilityService.get_scrape_schedule_file()
        self.scrape_boxscore_file = UtilityService.get_scrape_boxscore_file()
        self.scrape_playbyplay_file = UtilityService.get_scrape_playbyplay_file()
        self.metadata_file = UtilityService.get_metadata_file()

        self.config = config

        self.scrape()

        # build the boxscore data
        BoxscoreConsumerService(config).collect_boxscore_data()

        # build the playbyplay data
        PlaybyplayConsumerService(config).collect_playbyplay_data()

        # generate unified JSON structure in files
        CombineConsumerService(config).combine()

        # end __init__

    def scrape(self):
        do_scrape = self.config.get("do.scrape")
        if not do_scrape or do_scrape.strip().lower() != "y":
            self.logger.info("not scraping")
            return
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        for teamId in self.team_ids:
            metadata_file_path = os.path.join(self.output_dir, str(teamId), self.scrape_data_dir, self.metadata_file)
            FileService.delete_file(metadata_file_path)
            
            for season in self.seasons:
                scrape_schedule_dir = os.path.join(self.output_dir, str(teamId), self.scrape_data_dir, self.schedule_data_dir, str(season))
                os.makedirs(scrape_schedule_dir, exist_ok=True)
                FileService.delete_all_files_in_directory(scrape_schedule_dir)

                scrape_boxscore_dir = os.path.join(self.output_dir, str(teamId), self.scrape_data_dir, self.boxscore_data_dir, str(season))
                os.makedirs(scrape_boxscore_dir, exist_ok=True)
                FileService.delete_all_files_in_directory(scrape_schedule_dir)

                scrape_playbyplay_dir = os.path.join(self.output_dir, str(teamId), self.scrape_data_dir, self.playbyplay_data_dir, str(season))
                os.makedirs(scrape_playbyplay_dir, exist_ok=True)
                FileService.delete_all_files_in_directory(scrape_playbyplay_dir)

                season_results_url = self.season_results_url.replace("teamId", str(teamId))
                url = self.espn_url + season_results_url + str(season)
                self.logger.info(url)
                schedule_soup = RequestUtils(url, False).get_data()

                path = os.path.join(scrape_schedule_dir, self.scrape_schedule_file.replace("YYYY", str(season)))
                FileService.write_file(path, schedule_soup)

                # get game URLs
                links = schedule_soup.select('td.Table__TD span.ml4[data-testid="link"] a.AnchorLink')
                game_urls = [a["href"] for a in links]
                for url in game_urls:
                    self.logger.info(url)
                    try:
                        # get the game date
                        game_date_soup = RequestUtils(url, False).get_data()
                        game_date = self.extract_date(game_date_soup.get_text())
                        if game_date is None:
                            self.logger.info("No game date available, skipping")
                            continue

                        # collect the boxscore url page
                        gameId, boxscore_url = self.to_boxscore_url(url)
                        boxscore_soup = RequestUtils(boxscore_url, False).get_data()
                        boxscore_path = os.path.join(scrape_boxscore_dir, self.scrape_boxscore_file.replace("YYYYMMDD", str(game_date)))
                        FileService.write_file(boxscore_path, boxscore_soup)

                        # collect the play-by-play url page
                        # gameId already have
                        playbyplay_url = boxscore_url.replace("boxscore", "playbyplay")
                        playbyplay_soup = RequestUtils(playbyplay_url, False).get_data()
                        playbyplay_path = os.path.join(scrape_playbyplay_dir, self.scrape_playbyplay_file.replace("YYYYMMDD", str(game_date)))
                        FileService.write_file(playbyplay_path, playbyplay_soup)

                        metadata_file_path = os.path.join(self.output_dir, str(teamId), self.scrape_data_dir, self.metadata_file)

                        FileService.append(metadata_file_path, {
                            "season": season,
                            "game_date": game_date,
                            "gameId": gameId,
                            "boxscore_file": boxscore_path,
                            "boxscore_url": boxscore_url,
                            "playbyplay_url": playbyplay_url,
                            "playbyplay_file": playbyplay_path
                            }
                        )
                    except Exception as e:
                        self.logger.error(str(e))
    
    def to_boxscore_url(self, url):
        match = re.search(r'gameId/(\d+)', url)
        if not match:
            return None
        
        game_id = match.group(1)
        return game_id, self.espn_url + "boxscore/_/gameId/" + str(game_id)
    
    def extract_date(self, title_text):
        # Find the date inside parentheses, example: Mar 4, 2020
        match = re.search(r'\(([^)]+)\)', title_text)
        if not match:
            return None
        
        try:
            date_str = match.group(1)  # "Mar 4, 2020"

            # Convert to datetime object
            dt = datetime.strptime(date_str, "%b %d, %Y")

            # Return in YYYY-MM-DD format
            # return dt.strftime("%Y-%m-%d")
            return dt.strftime("%Y%m%d")
        except Exception as e:
            self.logger.error(str(e))
            return None

