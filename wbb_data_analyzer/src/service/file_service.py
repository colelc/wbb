import os
import stat
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

    # @staticmethod
    # def delete_file(filename:str):
    #     print("deleting file: " + str(filename))
    #     if os.path.exists(filename):
    #         deleted = os.remove(filename)
    #         print("deleted: " + str(deleted))

    @staticmethod
    def delete_file(filename):
        if os.path.exists(filename):
            try:
                # Clear read-only flag (Windows)
                os.chmod(filename, stat.S_IWRITE)
                os.remove(filename)
                #print(f"Deleted {filename}")
            except PermissionError:
                print(f"Permission denied: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
            # else:
            #     print(f"Still exists: {filename}")
        #else:
        #    print(filename + " does not exist")


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

        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        for f in files:
            full_path = os.path.join(directory, f)
            FileService.delete_file(full_path)  
