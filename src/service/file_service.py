import os
import csv
import json
from src.logging.app_logger import AppLogger

class FileService(object):

    @staticmethod
    def append(filename:str, obj):
        #logger = AppLogger.get_logger()
        #logger.info(str(filename) + " ")
        #logger.info(str(obj))
        with open(filename, "a") as f:
            f.write(json.dumps(obj) + "\n")

    @staticmethod
    def file_exists(filename:str) -> bool:
        #logger = AppLogger.get_logger()
        if os.path.exists(filename):
            #logger.info(filename + " exists")
            return True
        
        #logger.info(filename  + " does not exist")
        return False
    
    @staticmethod
    def write_file(filename:str, obj):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(obj))
