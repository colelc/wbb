import re
import os
from datetime import datetime
from src.logging.app_logger import AppLogger
from src.api.request_utils import RequestUtils
from src.service.file_service import FileService

class Scraper(object):
    def __init__(self, config):
        self.logger = AppLogger.get_logger()
        self.espn_url = config.get("espn.url")
        self.season_results_url = config.get("season.results.url")
        self.seasons = [season.strip() for season in config.get("seasons").split(",")]
        self.output_dir = config.get("output.data.dir")
        self.scrape_file = config.get("scrape.file")
        self.scrape_boxscore_file = config.get("scrape.boxscore.file")

        scrape_path = os.path.join(self.output_dir, "scrape")
        os.makedirs(scrape_path, exist_ok=True)
        for season in self.seasons:
            os.makedirs(os.path.join(scrape_path, str(season)), exist_ok=True)

        self.config = config

    def scrape(self):
        for season in self.seasons:
            url = self.espn_url + self.season_results_url + str(season)
            self.logger.info(url)
            soup = RequestUtils(url, False).get_data()

            # write out the complete scrape
            #scrape_file_path = os.path.join(self.output_dir, self.scrape_file.replace("YYYY", str(season)))
            #FileService.write_file(scrape_file_path, soup)

            # get game URLs
            links = soup.select('td.Table__TD span.ml4[data-testid="link"] a.AnchorLink')
            game_urls = [a["href"] for a in links]
            for url in game_urls:
                # get the game date
                game_date_soup = RequestUtils(url, False).get_data()
                game_date = self.extract_date(game_date_soup.get_text())

                # collect the boxscore url page
                boxscore_url = self.to_boxscore_url(url)
                boxscore_soup = RequestUtils(boxscore_url, False).get_data()
                boxscore_scrape_file_path = os.path.join(self.output_dir, "scrape", str(season), self.scrape_boxscore_file.replace("YYYYMMDD", str(game_date)))
                FileService.write_file(boxscore_scrape_file_path, boxscore_soup)
                
        return {}
    
    def to_boxscore_url(self, url):
        match = re.search(r'gameId/(\d+)', url)
        if not match:
            return None
        
        game_id = match.group(1)
        return self.espn_url + "boxscore/_/gameId/" + str(game_id)
    
    def extract_date(self, title_text):
        # Find the date inside parentheses, example: Mar 4, 2020
        match = re.search(r'\(([^)]+)\)', title_text)
        if not match:
            return None
        
        date_str = match.group(1)  # "Mar 4, 2020"

        # Convert to datetime object
        dt = datetime.strptime(date_str, "%b %d, %Y")

        # Return in YYYY-MM-DD format
        # return dt.strftime("%Y-%m-%d")
        return dt.strftime("%Y%m%d")

        # # letters
        # chalkboard_div = soup.select_one("div.spelling-bee-chalkboard")
        # FileService.write_file(self.letter_file_path, chalkboard_div)

        # letters = chalkboard_div.find_all(class_="chalkboard-letter")
        # letter_list = [letter.get_text().upper() for letter in letters]

        # # center letter (middle)
        # middle_dom = chalkboard_div.find(class_="center-letter")
        # middle = middle_dom.get_text().upper()

        # # pair list
        # pair_container_divs = soup.select('div.pair.letter-label')
        # pair_list = [pair_div.get_text().upper() for pair_div in pair_container_divs]
        # FileService.write_file(self.pair_file_path, pair_container_divs)

        # return {
        #     "letters" : letter_list,
        #     "middle": middle,
        #     "pairs": pair_list
        # }
    
