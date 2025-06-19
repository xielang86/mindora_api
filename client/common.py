import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    file_handler = RotatingFileHandler(
        'client.log',
        maxBytes=1024*1024*200, 
        backupCount=2
    )
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
