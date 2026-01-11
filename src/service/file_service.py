import os
import csv
import json
import shutil
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

    @staticmethod
    def delete_file(filename:str):
        if os.path.exists(filename):
            os.remove(filename)

    @staticmethod
    def read_file(filename: str):
        games_list = []
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    games_list.append(json.loads(line))
                    
        return games_list
    
    @staticmethod
    def read_all_files_in_directory(directory: str):
        data_list = list()
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        for f in files:
            data = FileService.read_file(os.path.join(directory, f))
            for d in data:
                data_list.append(d)

        return data_list
    
    @staticmethod
    def delete_all_files_in_directory(directory: str):
        log = AppLogger.get_logger()
        log.info("Deleting files from: " + str(directory))
        data_list = list()
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        for f in files:
            log.info("Deleting: " + str(f))
            FileService.delete_file(f)  
