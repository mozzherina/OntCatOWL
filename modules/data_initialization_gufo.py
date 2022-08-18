""" Implements functions for GUFO Data.
- Loading GUFO Data used for the evaluations from a YAML file and creates an output dictionary.
- Validate if the loaded data is correct.
"""
import yaml
from yaml import SafeLoader

from modules.logger_config import initialize_logger
from modules.utils_general import has_duplicates

# TODO (@pedropaulofb): These values must be updated when the YAML file is updated.
NUMBER_CLASSES_TYPES = 14
NUMBER_CLASSES_INDIVIDUALS = 13


def initialize_gufo_dictionary():
    """ Loads GUFO Data from a YAML resource file and returns a multi-level dictionary. The dictionary contains:
            - 1st level (e.g.: gufo_data):
                1a) Types hierarchy dictionary of GUFO classes
                1b) Individuals hierarchy dictionary of GUFO classes
                1c) Complements (disjoint_unions) dictionary of GUFO classes
            - 2nd level (e.g.: gufo_data["types"]):
                2a) Dictionary of classes belonging to the types' hierarchy (keys) and its associated lists (items)
                2b) Dictionary of classes belonging to the individuals' hierarchy(keys) and its associated lists(items)
                2c) GUFO classes (keys) and a list of its compliments (items)
            - 3rd level:
                3a) Three lists (is_list, can_list, not_list) with strings of GUFO classes for the types' hierarchy.
                3b) Three lists (same as above) with strings of GUFO classes for the individuals' hierarchy.
                3c) None.
    """

    logger = initialize_logger()

    gufo_data_file = "resources/gufo_data.yaml"
    logger.debug(f"Loading {gufo_data_file} file...")

    try:
        with open(gufo_data_file) as f:
            loaded_gufo_data = yaml.load(f, Loader=SafeLoader)
            logger.debug(f"Resource file {gufo_data_file} successfully loaded.")
    except OSError:
        logger.error(f"Could not load {gufo_data_file} file. Exiting program.")
        exit(1)

    validate_gufo_data(loaded_gufo_data)

    return loaded_gufo_data

    # TODO (@pedropaulofb): In the future the yaml file should be created automatically from the gufo.owl file


def validate_gufo_data(gufo_data):
    """ Validate the GUFO data loaded from the YAML resource file. """

    logger = initialize_logger()
    logger.debug("Performing validation of the GUFO data loaded from the YAML resource file...")

    # Verify if only the two necessary 1st level entries were loaded.
    num_entries = len(gufo_data.keys())
    if num_entries != 3:
        logger.error(f"Data provided in YAML file is invalid: "
                     f"number of 1st level entries is different from the expected. "
                     f"Expected 3 but found {num_entries}. "
                     f"Exiting program.")
        exit(1)

    # Verify if 1st level entries were loaded.
    verify_loaded_1st_level_entries(gufo_data, "types")
    verify_loaded_1st_level_entries(gufo_data, "individuals")
    verify_loaded_1st_level_entries(gufo_data, "complements")

    # Verify if the number of classes in the hierarchies are the expected number.
    verify_num_classes_hierarchy(gufo_data, "types")
    verify_num_classes_hierarchy(gufo_data, "individuals")

    # For each class in the hierarchies, verify if the sum of the items in its lists equals the expected number.
    verify_num_items_classes(gufo_data, "types")
    verify_num_items_classes(gufo_data, "individuals")

    # For each class in the hierarchies or complements, there must be no duplicates (inside a list or between lists).
    verify_repeated_classes_hierarchies(gufo_data, "types")
    verify_repeated_classes_hierarchies(gufo_data, "individuals")
    # TODO (@pedropaulofb): Create function verify_repeated_classes_complements(gufo_data)

    # TODO (@pedropaulofb): Create new verification: every element loaded at the lowest level (classes from lists)
    #  must be part of one of the hierarchies' lists (e.g., gufo:Kind readed from is_list of gufo:King must be present
    #  in the list of the classes read from the Type hierarchy.

    logger.debug("Validation of the GUFO data loaded from the YAML resource file successfully performed.")


def verify_loaded_1st_level_entries(gufo_data, entry):
    """ Verify if the argument hierarchy was loaded. """

    logger = initialize_logger()

    if entry not in gufo_data.keys():
        logger.error(f"Data provided in YAML resource file is invalid: "
                     f"{entry.upper()} 1ST LEVEL ENTRY not found. Exiting program.")
        exit(1)


def verify_num_classes_hierarchy(gufo_data, hierarchy):
    """ Verify if the number of classes in the argument hierarchy is the expected number. """
    logger = initialize_logger()

    number_classes = expected_number(hierarchy)

    length_types = len(gufo_data[hierarchy])
    if length_types != number_classes:
        logger.error(f"Data provided in YAML file is invalid: "
                     f"number of classes in the {hierarchy.upper()} HIERARCHY is different from the expected. "
                     f"Expected {number_classes} but found {length_types}. "
                     f"Exiting program.")
        exit(1)


def verify_num_items_classes(gufo_data, hierarchy):
    """ For each class in the argument hierarchy, verify if the sum of the items in its lists
    equals the expected number. """

    logger = initialize_logger()
    number_classes = expected_number(hierarchy)

    classes_list = list(gufo_data[hierarchy].keys())

    index = 0
    for it in classes_list:
        len_is_list = len(gufo_data[hierarchy][it]["is_list"])
        len_can_list = len(gufo_data[hierarchy][it]["can_list"])
        len_not_list = len(gufo_data[hierarchy][it]["not_list"])
        sum_len_lists = len_is_list + len_can_list + len_not_list
        if sum_len_lists != number_classes:
            logger.error(f"Data provided in YAML file is invalid: "
                         f"number of items in the {classes_list[index]} lists is different from the expected. "
                         f"Expected {number_classes} but found {sum_len_lists}. "
                         f"Exiting program.")
            exit(1)
        index += 1


def verify_repeated_classes_hierarchies(gufo_data, hierarchy):
    """ For each class in the argument hierarchy, there must be no duplicates (inside a list or between lists). """
    logger = initialize_logger()

    classes_list = list(gufo_data[hierarchy].keys())

    index = 0
    for it in classes_list:
        sum_list = gufo_data[hierarchy][it]["is_list"] \
                   + gufo_data[hierarchy][it]["can_list"] \
                   + gufo_data[hierarchy][it]["not_list"]
        if has_duplicates(sum_list):
            logger.error(f"Data provided in YAML file is invalid: "
                         f"Duplicated entry found in the lists for {classes_list[index]}. "
                         f"Exiting program.")
            exit(1)
        index += 1


def expected_number(hierarchy):
    """ Return the number of classes expected for the argument hierarchy. """

    logger = initialize_logger()
    number_classes = 0

    if hierarchy == "types":
        number_classes = NUMBER_CLASSES_TYPES
    elif hierarchy == "individuals":
        number_classes = NUMBER_CLASSES_INDIVIDUALS
    else:
        logger.error(f"Invalid parameter when returning expected number for {hierarchy.upper()} HIERARCHY. "
                     f"Exiting program.")
        exit(1)

    return number_classes
