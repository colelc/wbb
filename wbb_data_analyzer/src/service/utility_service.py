import os
from src.config.config import Config
from src.logging.app_logger import AppLogger

class UtilityService(object):

    config = None

    @staticmethod
    def set_up_config(config) -> dict:
        UtilityService.config = config

    @staticmethod
    def get_team_ids():
        return  [int(team_id.strip()) for team_id in UtilityService.config.get("team.ids").split(",")]
    
    @staticmethod
    def get_seasons():
        return [season.strip() for season in UtilityService.config.get("seasons").split(",")]
    
    @staticmethod
    def get_head_to_head_teams():
        return [int(team_id.strip()) for team_id in UtilityService.config.get("head.to.head").split(",")]
    
    @staticmethod
    def get_output_dir():
        return UtilityService.config.get("output.data.dir")
    
    @staticmethod
    def get_metadata_file():
        return UtilityService.config.get("metadata.file")
    
    @staticmethod
    def get_scrape_schedule_file():
        return UtilityService.config.get("scrape.schedule.file")
    
    @staticmethod
    def get_scrape_boxscore_file():
        return UtilityService.config.get("scrape.boxscore.file")
    
    @staticmethod
    def get_scrape_playbyplay_file():
        return UtilityService.config.get("scrape.playbyplay.file")
    
    @staticmethod
    def get_scrape_data_dir():
        return UtilityService.config.get("scrape.data.dir")
    
    @staticmethod
    def get_schedule_data_dir():
        return UtilityService.config.get("schedule.data.dir")
    
    @staticmethod
    def get_boxscore_data_dir():
        return UtilityService.config.get("boxscore.data.dir")
    
    @staticmethod
    def get_boxscore_data_file():
        return UtilityService.config.get("boxscore.data.file")
    
    @staticmethod
    def get_playbyplay_data_dir():
        return UtilityService.config.get("playbyplay.data.dir")
    
    @staticmethod
    def get_playbyplay_data_file():
        return UtilityService.config.get("playbyplay.data.file")
    
    @staticmethod
    def get_combined_data_dir():
        return UtilityService.config.get("combined.data.dir")
    
    @staticmethod
    def get_combined_data_file():
        return UtilityService.config.get("combined.data.file")