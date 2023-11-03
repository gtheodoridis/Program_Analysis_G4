import logging

logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("interpreter")
# flog_handler = logging.FileHandler('../logs/tags.log', mode="w")
# flog_handler.setFormatter(formatter)
# logger.addHandler(flog_handler)
