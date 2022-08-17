""" Loads GUFO data used for the evaluations. """

import yaml
from yaml import SafeLoader

from modules.logger_config import initialize_logger


def initialize_gufo():
    """ Initialize GUFO dictionary with types and individuals. """

    logger = initialize_logger()
    gufo_data_file = "../resources/gufo_data.yaml"

    try:
        with open(gufo_data_file) as f:
            loaded_data = yaml.load(f, Loader=SafeLoader)
    except OSError:
        logger.error(f"Could not load {gufo_data_file} file. Exiting program.")
        exit(1)

    return loaded_data
