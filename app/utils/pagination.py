from flask import request


def get_pagination_params():
    try:
        # get page from url default = 1
        # ensure page is at least 1
        page = max(1, int(request.args.get("page", 1)))
        # get per_page from url default = 10
        # ensure per_page at least 1
        # maximum per_page = 100
        per_page = min(100, max(1, int(request.args.get("per_page", 10))))
    except (ValueError, TypeError):
        page, per_page = 1, 10
    return page, per_page


# Apply pagination to database query
def paginate_query(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.total

# What .paginate() returns:
# An object with:
# items -> current page data
# total -> total records
# page -> total pages
# etc
