import requests
from src.logging.app_logger import AppLogger


class ApiUtils(object):

    @classmethod
    def check_for_api_error(cls, response):
        logger = AppLogger.get_logger()

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.info(str(response.text))
            # logger.info(str(response.url))
            logger.info(str(response))
            logger.info(str(response.__attrs__))
            logger.info(str(response.reason))
            logger.info(str(response._content))
            logger.info(str(response.reason))
            logger.info(str(response.request.__class__))
            raise

    @classmethod
    def debug(cls, response):
        logger = AppLogger.get_logger()

        #logger.info(str(response.text))
        logger.info(str(response.url))
        logger.info(str(response))
        logger.info(str(response.__attrs__))
        logger.info(str(response.reason))
        logger.info(str(response._content))
        logger.info(str(response.reason))
        logger.info(str(response.request.__class__))

  