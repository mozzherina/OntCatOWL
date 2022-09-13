""" Implementation of rules related to the GUFO types hierarchy. """
import time

from prettytable import PrettyTable

from modules.logger_config import initialize_logger
from modules.propagation import execute_and_propagate_down, execute_and_propagate_up
from modules.utils_dataclass import get_list_gufo_classification, get_element_list, external_move_to_is_list, \
    NEW_get_list_gufo_classification
from modules.utils_graph import get_all_related_nodes, get_subclasses, get_superclasses, get_all_superclasses, \
    get_all_subclasses

INTERVENTION_WARNING = "MANUAL INTERVENTION NEEDED!\n"

# Frequent GUFO types
GUFO_KIND = "gufo:Kind"
GUFO_SORTAL = "gufo:Sortal"
GUFO_NON_SORTAL = "gufo:NonSortal"


def rule_k_s_sup(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: All direct or indirect superclasses of an ontology class that is a type of gufo:Kind
                    cannot be a type of gufo:Sortal.
        Inverse of rule_s_k_sub.
    - DEFAULT: Automatic
    - CODE: k_s_sup
    """

    rule_code = "k_s_sup"
    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if GUFO_KIND in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")
            # The selected dataclass is included in the exclusion list because the action must not be performed on it.
            execute_and_propagate_up(list_ontology_dataclasses, graph, nodes_list,
                                     ontology_dataclass.uri,
                                     rule_code, [ontology_dataclass.uri])
            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_s_k_sub(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: All direct or indirect subclasses of an ontology class that is a type of gufo:Sortal
                    cannot be a type of gufo:Kind.
        Inverse of rule_k_s_sup.
    - DEFAULT: Automatic
    - CODE: s_k_sub
    """

    rule_code = "s_k_sub"
    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if GUFO_SORTAL in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")
            # The selected dataclass is included in the exclusion list because the action must not be performed on it.
            execute_and_propagate_down(list_ontology_dataclasses, graph, nodes_list,
                                       ontology_dataclass.uri, rule_code, [ontology_dataclass.uri])
            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_t_k_sup(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: If a class has a direct or indirect superclass that is a gufo:Kind, all others direct or indirect
                    superclasses are not gufo:Kinds.
    - DEFAULT: Automatic
    - CODE: t_k_sup
    """

    rule_code = "t_k_sup"
    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if GUFO_KIND in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

            # Get all subclasses
            all_subclasses = get_subclasses(graph, nodes_list["all"], ontology_dataclass.uri).copy()

            # For all subclasses
            for subclass in all_subclasses:
                # Get all superclasses
                all_superclasses_of_subclasses = get_superclasses(graph, nodes_list["all"], subclass).copy()
                # Return all superclasses that are of type Kind
                return_list = get_list_gufo_classification(list_ontology_dataclasses, all_superclasses_of_subclasses,
                                                           GUFO_KIND)
                counter = len(return_list)
                if counter != 1:
                    # TODO (@pedropaulofb): This error could be substituted by a warning and a possibility
                    #  of correction for the user
                    logger.error(f"Inconsistency detected. Number of gufo:Kinds types as supertypes "
                                 f"of {ontology_dataclass.uri} is {counter}, while it must be exactly 1. "
                                 f"Program aborted.")
                    exit(1)
                else:
                    # set all supertypes as NOT KIND (except for the one that is already a kind)
                    execute_and_propagate_up(list_ontology_dataclasses, graph, nodes_list, subclass,
                                             "t_k_sup",
                                             return_list)
            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_ns_s_sup(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: All direct or indirect superclasses of an ontology class that is a type of gufo:NonSortal
                    cannot be a type of gufo:Sortal.
        Inverse of rule_s_ns_sub.
    - DEFAULT: Automatic
    - CODE: ns_s_sup
    """

    rule_code = "ns_s_sup"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if GUFO_NON_SORTAL in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")
            execute_and_propagate_up(list_ontology_dataclasses, graph, nodes_list,
                                     ontology_dataclass.uri, rule_code, [ontology_dataclass.uri])
            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_s_ns_sub(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: All direct or indirect subclasses of an ontology class that is a type of gufo:Sortal
                    cannot be a type of gufo:NonSortal.
        Inverse of rule_ns_s_sup.
    - DEFAULT: Automatic
    - CODE: s_ns_sub
    """

    rule_code = "s_ns_sub"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if GUFO_SORTAL in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")
            execute_and_propagate_down(list_ontology_dataclasses, graph, nodes_list,
                                       ontology_dataclass.uri, rule_code, [ontology_dataclass.uri])
            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_r_ar_sup(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: No rigid or semi-rigid type can have an anti-rigid type as direct or indirect superclass.
        Inverse of rule_ar_r_sub.
    - DEFAULT: Automatic
    - CODE: r_ar_sup
    """

    rule_code = "r_ar_sup"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        # Getting RigidType or SemiRigidType types
        if ("gufo:RigidType" in ontology_dataclass.is_type) or ("gufo:SemiRigidType" in ontology_dataclass.is_type):
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

            # No RigidType or SemiRigidType can have AntiRigidType as direct or indirect superclasses and (... cont.)
            execute_and_propagate_up(list_ontology_dataclasses, graph, nodes_list,
                                     ontology_dataclass.uri,
                                     rule_code, [ontology_dataclass.uri])

            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_ar_r_sub(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: No AntiRigidType can have RigidType or SemiRigidType as direct or indirect subclasses.
        Inverse of rule_r_ar_sup.
    - DEFAULT: Automatic
    - CODE: ar_r_sub
    """

    rule_code = "ar_r_sub"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if "gufo:AntiRigidType" in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

            execute_and_propagate_down(list_ontology_dataclasses, graph, nodes_list,
                                       ontology_dataclass.uri, rule_code, [ontology_dataclass.uri])

            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_n_r_t(list_ontology_dataclasses, nodes_list):
    """
    - CAUSE: Every type must supply (Kinds) or carry (Non-Kind Sortals) a single identity principle or
    aggregate (NonSortals) multiple identity principles.

    - CONSEQUENCE: In complete models, every type without supertypes and without subtypes must be a gufo:Kind.

    - BEHAVIOUR:

        - Complete + Automatic Only: Enforce. (IMPLEMENTED)
        - Complete + Automatic: Enforce. (IMPLEMENTED)
        - Complete + Interactive: Ask user: apply or deficiency. (NOT IMPLEMENTED)

        - Incomplete + Automatic Only: Not available. No action. (NOT IMPLEMENTED)
        - Incomplete + Automatic: Ask user: apply or include. (NOT IMPLEMENTED)
        - Incomplete + Interactive: Ask user: apply or include. (NOT IMPLEMENTED)
    """

    rule_code = "n_r_t"
    gufo_kind = GUFO_KIND

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if gufo_kind not in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

            if (ontology_dataclass.uri in nodes_list["roots"]) and (ontology_dataclass.uri in nodes_list["leaves"]):
                if gufo_kind in ontology_dataclass.can_type:
                    ontology_dataclass.move_element_to_is_list(gufo_kind)
                else:
                    # TODO (@pedropaulofb): Interact with user: (a) create class or relaton or (b) reclassify.
                    logger.error(f"Cannot set class {ontology_dataclass.uri} as {gufo_kind}. "
                                 f"Inconsistency detected. Program aborted.")
                    exit(1)

            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_ns_s_spe(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: A NonSortal must be directly or indirectly specialized by a Sortal OR it must directly or indirectly
                    specialize another NonSortal that is directly or indirectly specialized by a Sortal.
    - DEFAULT: Interactive
    - CODE: ns_s_spe
    """
    # TODO (@pedropaulofb): The complete user interactions for treating this rule must be:
    #   a) Show to user only classes that CAN BE Sortals.
    #       a1) User can set one of them as Sortal.
    #       a2) User can specialize it with a new Sortal.
    #   b) Show to user only classes that ARE NonSortals.
    #       b1) User can reclassify one of them as Sortal.
    #       b2) User can specialize it with a new Sortal.

    # TODO (@pedropaulofb): The special case of a NonSortal single class (root and leaf at the same time)
    #  must be treated. In this case,
    #   (a) the user must input a new Sortal class specializing it,
    #   (b) create a specialization relation between an already existent class and this NonSortal class, and
    #   (c) modify the classification of the single class.

    rule_code = "ns_s_spe"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:
        if GUFO_NON_SORTAL in ontology_dataclass.is_type:
            logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

            # Get all ontology dataclasses that are reachable from the input dataclass
            list_related_nodes = get_all_related_nodes(graph, nodes_list, ontology_dataclass.uri)
            logger.debug(f"Related nodes of {ontology_dataclass.uri} are: {list_related_nodes}")

            # Check if one of these related dataclasses is a gufo:Sortal
            sortal_list = get_list_gufo_classification(list_ontology_dataclasses, list_related_nodes, GUFO_SORTAL)

            if len(sortal_list) == 0:
                logger.debug(f"None of the nodes related to from {ontology_dataclass.uri} is a gufo:Sortal")

                logger.info(INTERVENTION_WARNING)
                time.sleep(0.2)

                print(f"\nFor {ontology_dataclass.uri}, one of the following related classes must be a gufo:Sortal "
                      f"or must be specialized by a gufo:Sortal:")

                table = PrettyTable(['URI', 'Known IS Types', "Known NOT Types"])

                for related_node in list_related_nodes:
                    related_node_is_types = get_element_list(list_ontology_dataclasses, related_node, "is_type")
                    related_node_not_types = get_element_list(list_ontology_dataclasses, related_node, "not_type")
                    table.add_row([related_node, related_node_is_types, related_node_not_types])

                table.align = "l"
                print(table)

                new_sortal_uri = input("Enter the URI of the element to be classified as a Sortal: ")
                new_sortal_uri.strip()
                new_sortal_type = "gufo:" + input("Enter the type of the element (options are: "
                                                  "Sortal, Kind, Phase, Role, or SubKind): ")
                new_sortal_type.strip()

                # TODO (@pedropaulofb): Treat invalid input from user (for both data entries).

                external_move_to_is_list(list_ontology_dataclasses, new_sortal_uri, new_sortal_type)

            logger.debug(f"Rule {rule_code} successfully concluded for ontology dataclass {ontology_dataclass.uri}.")


def rule_nk_k_sup(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: Every non-Kind Sortal must have a Kind as direct or indirect supertype.
                    I.e., there must be an identity provider for them.
                    Non-Kind Sortal = is_type: Sortal AND not_type: Kind
    - DEFAULT: Interactive
    - CODE: nk_k_sup
    """

    rule_code = "nk_k_sup"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:

        # CONDITION 1: class has is_type Sortal and not_type Kind:
        if (GUFO_SORTAL not in ontology_dataclass.is_type) or (GUFO_KIND not in ontology_dataclass.not_type):
            continue

        logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

        # Get all ontology dataclasses that are directly or indirectly superclasses of ontology_dataclass
        list_superclasses = get_all_superclasses(graph, nodes_list, ontology_dataclass.uri)
        logger.debug(f"Superclasses from {ontology_dataclass.uri} are: {list_superclasses}")

        # Verify if there is a Kind in the superclass list
        kind_sortals = get_list_gufo_classification(list_ontology_dataclasses, list_superclasses, GUFO_KIND)

        # CONDITION 2: Kind not found in list of superclasses
        if len(kind_sortals) != 0:
            continue

        list_possibilities = []
        # select which can be kind (can_type)
        for possible_kind in list_superclasses:

            possible_kind_can = get_element_list(list_ontology_dataclasses, possible_kind, "can_type")

            if GUFO_KIND in possible_kind_can:
                list_possibilities.append(possible_kind)

            # TODO (@pedropaulofb): Treat the case where there is no possibility (e.g., root class or a class
            # that all supertypes are have kind in its not_type list. In this case an incompleteness was found
            # and the user must (a) create a new kind class and define its relation with one of the classes in
            # the list_superclasses or (b) reclassify one of the classes.

        # If automatic, then the unique possibility can be directly asserted.
        # TODO (@pedropaulofb): Treat case not automatic.
        if len(list_possibilities) == 1:
            external_move_to_is_list(list_ontology_dataclasses, list_possibilities[0], GUFO_KIND)
            logger.debug(f"Class {list_possibilities[0]} is the unique possible identity provider "
                         f"for {ontology_dataclass.uri}. Hence, it was automatically asserted as gufo:Kind.")

        # Case multiple possibilities, user must choose.
        elif len(list_possibilities) > 1:

            logger.info(INTERVENTION_WARNING)
            time.sleep(0.2)

            # User must choose an option to become a Kind.
            print(f"No identity provider (Kind) was identified for the class {ontology_dataclass.uri}.")
            print(f"The following classes were identified as possible identity providers:")
            for item in list_possibilities:
                print(f"\t - {item}")
            new_kind = input(f"Enter the class to be set as gufo:Kind: ")
            new_kind.strip()
            external_move_to_is_list(list_ontology_dataclasses, new_kind, GUFO_KIND)

            # TODO (@pedropaulofb): Instead of just selecting a possibility, the user can create
            #  a new one and set the relation or to reclassify one of the classes.


# TODO (@pedropaulofb): RESTRICT LIST OF POSSIBILITIES FOR SHOWING ONLY ALLOWED CLASSES!
def rule_ns_k_sub(list_ontology_dataclasses, graph, nodes_list):
    """
    - DESCRIPTION: NonSortals aggregates identities from at least two different identity principles providers.
                    Hence, every NonSortal must have at least two Kind as direct or indirect subclasses.

    !!!!!!!!  REVIEW        For this function, the user must set one Kind at a time, allowing the tool to perform the inferences and types
        discoveries based on this type assertion. When two Kinds are necessaries, the user is going to assert a single
        one and just in the next function call the second kind is going to be requested.
    """

    rule_code = "ns_k_sub"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:

        # CONDITION 1: Ontology dataclass has gufo:NonSortal in its is_type list.
        if GUFO_NON_SORTAL not in ontology_dataclass.is_type:
            continue

        logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

        # Get list of all subclasses up to leaves.
        all_subclasses = get_all_subclasses(graph, nodes_list, ontology_dataclass.uri)

        # Count the number of subclasses that are kinds.
        kind_subclasses = get_list_gufo_classification(list_ontology_dataclasses, all_subclasses, GUFO_KIND)
        number_of_kinds = len(kind_subclasses)

        # Treat if number of kind subclasses is smaller than 2.
        if number_of_kinds < 2:

            logger.info(INTERVENTION_WARNING)
            time.sleep(0.2)

            # Subclasses that can be kind
            list_can_kind_subclasses = NEW_get_list_gufo_classification(list_ontology_dataclasses, all_subclasses,
                                                                        "CAN", GUFO_KIND)

            # CONDITION: If there is not enough options
            if (number_of_kinds + len(list_can_kind_subclasses)) < 2:
                logger.error(f"Not enough options to be classified as Kinds for {ontology_dataclass.uri}. "
                             f"Inconsistency found. Exiting program.")
                exit(1)

            print(f"The class {ontology_dataclass.uri} is a NonSortal with {number_of_kinds} Kind as subclass. "
                  f"NonSortals aggregates identities from at least two different identity principles providers. "
                  f"Hence, every NonSortal must have at least two Kind as direct or indirect subclasses. ")

            print(f"For {ontology_dataclass.uri}, the subclasses that can be set as gufo:Kinds are:")

            for can_kind_subclass in list_can_kind_subclasses:
                print(f"\t - {can_kind_subclass}")

            new_kind = input(f"Enter the class to be set as gufo:Kind: ")
            new_kind.strip()
            external_move_to_is_list(list_ontology_dataclasses, new_kind, GUFO_KIND)
            logger.debug(f"Subclass {new_kind} successfully defined as gufo:Kind for "
                         f"ontology dataclass {ontology_dataclass.uri}.")


def rule_s_nsup_k(list_ontology_dataclasses, graph, nodes_list):
    """
        - CAUSE: Every Sortal (types that carry or supply an identity principle) must have exactly
        one identity principle, which is provided by a Kind.

        - CONSEQUENCE: In complete models, every gufo:Sortal without supertypes is a gufo:Kind.

        - BEHAVIOUR:

            - Complete + Automatic Only: Enforce. (IMPLEMENTED)
            - Complete + Automatic: Enforce. (IMPLEMENTED)
            - Complete + Interactive: Ask user: apply or deficiency. (NOT IMPLEMENTED)

            - Incomplete + Automatic Only: Not available. No action. (NOT IMPLEMENTED)
            - Incomplete + Automatic: Ask user: apply or include. (NOT IMPLEMENTED)
            - Incomplete + Interactive: Ask user: apply or include. (NOT IMPLEMENTED)
        """

    rule_code = "s_nsup_k"

    logger = initialize_logger()

    for ontology_dataclass in list_ontology_dataclasses:

        # CONDITION 1: ontology_dataclass must be a gufo:Sortal
        if GUFO_SORTAL not in ontology_dataclass.is_type:
            continue

        logger.debug(f"Starting rule {rule_code} for ontology dataclass {ontology_dataclass.uri}...")

        # Get list of all superclasses up to leaves.
        all_superclasses = get_all_superclasses(graph, nodes_list, ontology_dataclass.uri)

        # CONDITION 2: list of superclasses must be empty

        if len(all_superclasses) == 0:
            ontology_dataclass.move_element_to_is_list(GUFO_KIND)
