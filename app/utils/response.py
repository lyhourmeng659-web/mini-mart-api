from flask import jsonify


# Status 200 Success
def success_response(data=None, message="Success", status_code=200):
    response = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(response), status_code


# Status Error 400 bad request
def error_response(message="An error occurred", status_code=400, errors=None):
    response = {
        "success": False,
        "message": message,
        "data": errors if errors else {}
    }
    return jsonify(response), status_code


def paginated_response(items, total, page, per_page, message="Success"):
    return success_response({
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    }, message)
