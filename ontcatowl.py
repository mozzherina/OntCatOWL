""" Main module  for OntCatOWL """
import time
from datetime import datetime

from modules.dataclass_verifications import verify_all_ontology_dataclasses_consistency
from modules.graph_save_ontology import save_ontology_file, save_ontology_gufo_statements
from modules.initialization_arguments import treat_arguments
from modules.initialization_data_graph import initialize_nodes_lists
from modules.initialization_data_gufo_dictionary import initialize_gufo_dictionary
from modules.initialization_data_ontology_dataclass import initialize_ontology_dataclasses, load_known_gufo_information
from modules.logger_config import initialize_logger
from modules.report_printer import print_report_file
from modules.results_calculation import generates_partial_statistics_list, calculate_final_statistics
from modules.results_screen_printer import print_statistics_screen
from modules.rules_types_run import execute_rules_types
from modules.utils_rdf import load_graph_safely, perform_reasoning

SOFTWARE_VERSION = "OntCatOWL - Identification of Ontological Categories for OWL Ontologies\n" \
                   "Version 0.20221101 - https://github.com/unibz-core/OntCatOWL/\n"

if __name__ == "__main__":

    # DATA LOADINGS AND INITIALIZATIONS

    st = time.perf_counter()
    global_configurations = treat_arguments(SOFTWARE_VERSION)

    logger = initialize_logger()

    now = datetime.now()
    start_date_time = now.strftime("%d-%m-%Y %H:%M:%S")
    logger.info(f"OntCatOWL started on {start_date_time}!")

    # Loading owl ontologies from files to the working memory
    ontology_graph = load_graph_safely(global_configurations["ontology_path"])
    gufo_graph = load_graph_safely("resources/gufoEndurantsOnly.ttl")

    # Loading GUFO dictionary from yaml file
    gufo_dictionary = initialize_gufo_dictionary()

    if global_configurations["reasoning"]:
        perform_reasoning(ontology_graph)

    ontology_dataclass_list = initialize_ontology_dataclasses(ontology_graph, gufo_dictionary)
    verify_all_ontology_dataclasses_consistency(ontology_dataclass_list)

    ontology_nodes = initialize_nodes_lists(ontology_graph)

    # Loading the GUFO information already known from the ontology
    load_known_gufo_information(ontology_graph, gufo_graph, ontology_dataclass_list)
    before_statistics = generates_partial_statistics_list(ontology_dataclass_list)

    # EXECUTION

    execute_rules_types(ontology_dataclass_list, ontology_graph, ontology_nodes, global_configurations)

    # SAVING RESULTS - OUTPUT

    after_statistics = generates_partial_statistics_list(ontology_dataclass_list)
    ontology_graph = save_ontology_gufo_statements(ontology_dataclass_list, ontology_graph)

    # In this version of OntCatOWL, only types are executed and, hence, only them should be printed/reported.
    statistics = calculate_final_statistics(before_statistics, after_statistics)
    print_statistics_screen(statistics, "TYPES_ONLY")

    now = datetime.now()
    end_date_time_here = now.strftime("%d-%m-%Y %H:%M:%S")
    end_date_time = now.strftime("%Y.%m.%d-%H.%M.%S")
    et = time.perf_counter()
    elapsed_time = round((et - st), 3)
    logger.info(f"OntCatOWL concluded on {end_date_time_here}! Total execution time: {elapsed_time} seconds.")

    print_report_file(ontology_dataclass_list, start_date_time, end_date_time_here, end_date_time, elapsed_time,
                      global_configurations, before_statistics, after_statistics, "TYPES_ONLY")

    if global_configurations["import_gufo"]:
        united_graph = ontology_graph + gufo_graph
        save_ontology_file(end_date_time, ontology_graph, global_configurations)
    else:
        save_ontology_file(end_date_time, ontology_graph, global_configurations)

# TODO (@pedropaulofb): IMPROVEMENTS
# Instead of using exit(1) for all problems, identify which ones can generate a warning instead.
# Create a (much) better deficiency (incompleteness)(inconsistency?) report.
# Hash is generated differently when list is [A, B] and [B, A]. So maybe is the case to keep it always sorted.
# Create argument for cleaning all generated logs and reports (e.g., ontcatowl.py --clean)
# Create a verbose mode where all INFOs are printed. DEBUG is always only printed in the log file.
# Create menus for better user interactions: https://pypi.org/project/simple-term-menu/
# At the report, after execution, create lists of classes that were improved or not for a better user identification.
# OPTION TO SAVE NEGATIVE DISCOVERIES!!!

# TODO (@pedropaulofb): PERFORMANCE
# Insert "break" after moving commands (name == class.uri) because there are no repetitions. Verify for/break statement

# TODO (@pedropaulofb): BEFORE RELEASE OF VERSION
# Evaluate on Linux before release first version
# Verify if there is any unused module, function or methods
# Move TO DO comments from this module to GitHub issues
# Evaluate all Lints from all modules
