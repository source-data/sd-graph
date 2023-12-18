from neoflask.cache import cache
from neoflask.queries import DESCRIBE_PUBLISHERS, DESCRIBE_REVIEWING_SERVICES_V2
from neotools import ask_neo


@cache.cached()
def publishers_get():  # noqa: E501
    """Get information about available publishers.

     # noqa: E501


    :rtype: List[PublisherDescription]
    """
    return ask_neo(DESCRIBE_PUBLISHERS())


@cache.cached()
def reviewing_services_get():  # noqa: E501
    """Get information about available reviewing services

     # noqa: E501


    :rtype: ReviewingServiceCollection
    """
    return ask_neo(DESCRIBE_REVIEWING_SERVICES_V2())
