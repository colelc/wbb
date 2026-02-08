import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService
from src.service.scrape.boxscore_consumer_service import BoxscoreConsumerService
from src.service.scrape.playbyplay_consumer_service import PlaybyplayConsumerService
from src.service.scrape.combine_consumer_service import CombineConsumerService

class Scraper(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.espn_url = config.get("espn.url")
        self.team_id = config.get("team.id")
        self.season_results_url = config.get("season.results.url").replace("teamId", self.team_id)
        self.seasons = [season.strip() for season in config.get("seasons").split(",")]
        self.output_dir = config.get("output.data.dir")
        os.makedirs(self.output_dir, exist_ok=True)

        self.scrape_schedule_file = config.get("scrape.schedule.file")
        self.scrape_boxscore_file = config.get("scrape.boxscore.file")
        self.scrape_playbyplay_file = config.get("scrape.playbyplay.file")
        metadata_file = config.get("metadata.file")
        self.metadata_file_path = os.path.join(self.output_dir, metadata_file)

        scrape_schedule_path = os.path.join(self.output_dir, "scrape", "schedule")
        os.makedirs(scrape_schedule_path, exist_ok=True)

        scrape_boxscore_path = os.path.join(self.output_dir, "scrape", "boxscore")
        os.makedirs(scrape_boxscore_path, exist_ok=True)

        scrape_playbyplay_path = os.path.join(self.output_dir, "scrape", "playbyplay")
        os.makedirs(scrape_playbyplay_path, exist_ok=True)

        for season in self.seasons:
            os.makedirs(os.path.join(scrape_schedule_path, str(season)), exist_ok=True)
            os.makedirs(os.path.join(scrape_boxscore_path, str(season)), exist_ok=True)
            os.makedirs(os.path.join(scrape_playbyplay_path, str(season)), exist_ok=True)

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
        
        FileService.delete_file(self.metadata_file_path)
        
        games = dict()

        for season in self.seasons:
            url = self.espn_url + self.season_results_url + str(season)
            self.logger.info(url)
            schedule_soup = RequestUtils(url, False).get_data()

            scrape_schedule_file_path = os.path.join(self.output_dir, "scrape", "schedule", str(season), self.scrape_schedule_file.replace("YYYY", str(season)))
            FileService.write_file(scrape_schedule_file_path, schedule_soup)

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
                    boxscore_scrape_file_path = os.path.join(self.output_dir, "scrape", "boxscore", str(season), self.scrape_boxscore_file.replace("YYYYMMDD", str(game_date)))
                    if not FileService.file_exists(boxscore_scrape_file_path):
                        FileService.write_file(boxscore_scrape_file_path, boxscore_soup)

                    # collect the play-by-play url page
                    # gameId already have
                    playbyplay_url = boxscore_url.replace("boxscore", "playbyplay")
                    playbyplay_soup = RequestUtils(playbyplay_url, False).get_data()
                    playbyplay_scrape_file_path = os.path.join(self.output_dir, "scrape", "playbyplay", str(season), self.scrape_playbyplay_file.replace("YYYYMMDD", str(game_date)))
                    if not FileService.file_exists(playbyplay_scrape_file_path):
                        FileService.write_file(playbyplay_scrape_file_path, playbyplay_soup)

                    FileService.append(self.metadata_file_path, {
                        "season": season,
                        "game_date": game_date,
                        "gameId": gameId,
                        "boxscore_file": boxscore_scrape_file_path,
                        "boxscore_url": boxscore_url,
                        "playbyplay_url": playbyplay_url,
                        "playbyplay_file": playbyplay_scrape_file_path
                        }
                    )
                except Exception as e:
                    self.logger.error(str(e))
                

        return
    
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

