from neoflask.queries import DESCRIBE_REVIEWING_SERVICES_V2
from neotools import ask_neo


def reviewing_services_get():  # noqa: E501
    """Get information about available reviewing services

     # noqa: E501


    :rtype: ReviewingServiceCollection
    """
    return ask_neo(DESCRIBE_REVIEWING_SERVICES_V2())
