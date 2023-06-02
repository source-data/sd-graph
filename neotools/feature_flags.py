"""
Feature flags for enabling/disabling certain features.

Use cases are e.g. new smtag models which need to be tested in staging before being rolled out to production.
"""

import os

def _is_feature_flag_enabled(flag_name):
    return os.getenv(flag_name) == "true"


def is_auto_summarization_enabled():
    """Returns True if auto summarization is enabled, False otherwise."""
    return _is_feature_flag_enabled("FEATURE_FLAG_AUTO_SUMMARIZATION")
