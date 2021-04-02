import logging
import sys

class Logger:
    def __init__(self, logger_name='default_logger', level='INFO') -> None:
        self.logger_name = logger_name
        self.level = level
    
    def setup_logger(self):
        logger = logging.getLogger(self.logger_name)

        if len(logger.handlers) == 0:
            logger.setLevel(self.level)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(self.level.upper())
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.info(f"Logger '{self.logger_name}' has been created and configured")
        
        return logger
