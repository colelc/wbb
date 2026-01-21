# #import os 
# import socket
# import sys
# from dotenv import dotenv_values

# class Config(object):
#     config = None

#     @staticmethod
#     def set_up_config(config_file_path:str) -> dict:

#         try:
#             host_name = socket.gethostname()
#             host_ip = socket.gethostbyname(host_name)
#         except Exception as e:
#             print(str(e))
#             sys.exit(99)

#         config = dotenv_values(config_file_path)
 
#         Config.config = config
#         return Config.config

#     @staticmethod
#     def get_property(key:str) -> str:
#         return Config.get_config().get(key)
    
#     @staticmethod
#     def get_config():
#         return Config.config
    
# #Config.get_config()