from flask import Blueprint
from app.services.category_service import CategoryService
from app.utils.response import success_response

front_category_bp = Blueprint("front_category", __name__)


@front_category_bp.route("", methods=["GET"])
def list_categories():
    categories, _ = CategoryService.get_all_active()
    return success_response([c.to_dict() for c in categories])
