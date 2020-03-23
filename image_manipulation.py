import logging
import logging.config
from json import load as jload

# Configure logger lg with config for appLogger from config.json["logging"]
with open('config.json', 'r') as f:
    config = jload(f)
    logging.config.dictConfig(config["logging"])
lg = logging.getLogger('appLogger')
# lg.debug('Log starts here')