from connexion import problem
from math import ceil
from neoflask.cache import cache
from neoflask.queries import REFEREED_PREPRINTS_V2, REFEREED_PREPRINT_V2
from neotools import ask_neo
from urllib.parse import urlencode


@cache.memoize()  # memoize handles function parameters, cached does not
def paper_get(doi=None, slug=None):  # noqa: E501
    """Get details about a refereed preprint by DOI or slug.

     # noqa: E501

    :param doi: The DOI of the refereed preprint. Either the DOI or the slug parameter must be specified.
    :type doi: str
    :param slug: The slug of the refereed preprint. Either the DOI or the slug parameter must be specified.
    :type slug: str

    :rtype: RefereedPreprint
    """
    if (not doi and not slug) or (doi and slug):
        return problem(status=400, title="Bad Request", detail="Must specify either doi or slug")
    result = ask_neo(REFEREED_PREPRINT_V2(), doi=doi, slug=slug)
    return result[0]["refereed_preprint"] if result else None


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


@cache.memoize()  # memoize handles function parameters, .cached does not
def papers_get(reviewed_by=None, query=None, published_in=None, page=None, per_page=None, sort_by=None, sort_order=None):  # noqa: E501
    """Get paginated collections of refereed preprints, optionally filtered by reviewing service

     # noqa: E501

    :param reviewed_by: The IDs of the reviewing services for which refereed preprints are requested. If specified, only refereed preprints that were reviewed by at least one of the specified reviewing services are returned. Is combined with the query and publishedIn parameters using a logical AND. If not specified, this filter is not applied.
    :type reviewed_by: List[str]
    :param query: A search string to filter the results by. The search string is matched against the refereed preprint DOI, title, abstract, and authors. The search is case-insensitive and matches partial words (e.g. the search string \&quot;covid\&quot; would match \&quot;COVID-19\&quot;). Is combined with the reviewedBy and publishedIn parameters using a logical AND. If not specified, this filter is not applied.
    :type query: str
    :param published_in: The journals to filter the results by. If specified, only refereed preprints that were published in at least one of the specified journals are returned. Is combined with the reviewedBy and query parameters using a logical AND. If not specified, this filter is not applied.
    :type published_in: List[str]
    :param page: The page number of the results to retrieve. The first page is 1.
    :type page: int
    :param per_page: The number of results to return per page.
    :type per_page: int
    :param sort_by: The field to sort the results by.
    :type sort_by: dict | bytes
    :param sort_order: The direction to sort the results in.
    :type sort_order: dict | bytes

    :rtype: InlineResponse200
    """
    lucene_query = _to_lucene_query(query) if query else None
    db_page = page - 1  # neo4j pages are 0-indexed, page is checked for > 0 in param validation
    db_sort_by = ({
        "preprint-date": "preprint_date",
        "reviewing-date": "review_date",
    }).get(sort_by)
    sort_ascending = sort_order == "asc"
    db_params = dict(
        reviewed_by=reviewed_by,  # parameterized in database query, no need to escape
        lucene_query=lucene_query,  # user input is escaped in _to_lucene_query()
        published_in=published_in,  # parameterized in database query, no need to escape
        page=db_page,  # converted from 1- to 0-indexed above
        per_page=per_page,  # already validated, and can be passed through
        sort_by=db_sort_by,
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
