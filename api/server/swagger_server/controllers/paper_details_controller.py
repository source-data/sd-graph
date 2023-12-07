from math import ceil
from neoflask.queries import REFEREED_PREPRINTS_V2
from neotools import ask_neo
from urllib.parse import urlencode

def _to_lucene_query(user_input):
    # remove double quotes and backslashes from user input to prevent injection
    escaped = user_input.replace('"', "").replace("\\", "")
    # surround with double quotes for exact query
    return f'"{escaped}"'


def papers_url(reviewed_by=None, query=None, page=None, per_page=None, sort_by=None, sort_order=None):
    base_url = "/api/v2/papers/"
    query_params_list = [
        ("page", page),
        ("perPage", per_page),
        ("sortBy", sort_by),
        ("sortOrder", sort_order),
    ]
    if reviewed_by:
        for service in reviewed_by:
            query_params_list.append(("reviewedBy", service))
    if query:
        query_params_list.append(("query", query))

    query_params = urlencode(query_params_list)
    return f"{base_url}?{query_params}"


def papers_get(reviewed_by=None, query=None, page=None, per_page=None, sort_by=None, sort_order=None):  # noqa: E501
    """Get paginated collections of papers, optionally filtered by reviewing service

     # noqa: E501

    :param reviewed_by: The IDs of the reviewing services for which papers are requested.
    :type reviewed_by: List[str]
    :param query: A search string to filter the results by.
    :type query: str
    :param page: The page number of the results to retrieve. The first page is 1.
    :type page: int
    :param per_page: The number of results to return per page.
    :type per_page: int
    :param sort_by: The field to sort the results by.
    :type sort_by: str
    :param sort_order: The direction to sort the results in.
    :type sort_order: str

    :rtype: InlineResponse200
    """
    lucene_query = _to_lucene_query(query) if query else None
    db_page = page - 1  # neo4j pages are 0-indexed, page is checked for > 0 in param validation
    sort_ascending = sort_order == "asc"
    db_params = dict(
        reviewed_by=reviewed_by,  # parameterized in database query, no need to escape
        lucene_query=lucene_query,  # user input is escaped in _to_lucene_query()
        page=db_page,  # converted from 1- to 0-indexed above
        # remaining parameters are already validated and can be passed through
        per_page=per_page,
        sort_by=sort_by,
        sort_ascending=sort_ascending
    )
    result = ask_neo(REFEREED_PREPRINTS_V2(), **db_params)
    n_total = result[0]["n_total"]
    n_pages = int(ceil(n_total / per_page))
    show_prev = page > 1 and page <= n_pages
    show_next = page < n_pages and page >= 1

    return {
        "items": result[0]["items"],
        "paging": {
            "first": papers_url(reviewed_by, query, 1, per_page, sort_by, sort_order),
            "prev": papers_url(reviewed_by, query, max(1, page - 1), per_page, sort_by, sort_order) if show_prev else None,
            "current": papers_url(reviewed_by, query, page, per_page, sort_by, sort_order),
            "next": papers_url(reviewed_by, query, min(n_pages, page + 1), per_page, sort_by, sort_order) if show_next else None,
            "last": papers_url(reviewed_by, query, n_pages, per_page, sort_by, sort_order),
            "currentPage": page,
            "totalPages": n_pages,
            "perPage": per_page,
            "totalItems": n_total,
            "sortedBy": sort_by,
            "sortedOrder": sort_order,
        }
    }
