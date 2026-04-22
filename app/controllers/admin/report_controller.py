from flask import Blueprint, request
from app.services.report_service import ReportService
from app.middleware.auth_middleware import admin_required
from app.utils.response import success_response, error_response

admin_report_bp = Blueprint("admin_report", __name__)


def _get_period_params():
    period = request.args.get("period", "monthly")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    return period, start_date, end_date


@admin_report_bp.route("/sales", methods=["GET"])
@admin_required
def sales_summary():
    period, start_date, end_date = _get_period_params()
    data, err = ReportService.sales_summary(period=period, start_date=start_date, end_date=end_date)
    if err:
        return error_response(err, 400)
    return success_response(data, "Sales summary")


@admin_report_bp.route("/sales/daily", methods=["GET"])
@admin_required
def daily_sales():
    data, err = ReportService.sales_summary(period="daily")
    if err:
        return error_response(err, 400)
    return success_response(data, "Daily sales")


@admin_report_bp.route("/sales/weekly", methods=["GET"])
@admin_required
def weekly_sales():
    data, err = ReportService.sales_summary(period="weekly")
    if err:
        return error_response(err, 400)
    return success_response(data, "Weekly sales")


@admin_report_bp.route("/sales/monthly", methods=["GET"])
@admin_required
def monthly_sales():
    data, err = ReportService.sales_summary(period="monthly")
    if err:
        return error_response(err, 400)
    return success_response(data, "Monthly sales")


@admin_report_bp.route("/sales/by-product", methods=["GET"])
@admin_required
def sales_by_product():
    period, start_date, end_date = _get_period_params()
    data, err = ReportService.sales_by_product(period=period, start_date=start_date, end_date=end_date)
    if err:
        return error_response(err, 400)
    return success_response(data, "Sales by product")


@admin_report_bp.route("/sales/by-category", methods=["GET"])
@admin_required
def sales_by_category():
    period, start_date, end_date = _get_period_params()
    data, err = ReportService.sales_by_category(period=period, start_date=start_date, end_date=end_date)
    if err:
        return error_response(err, 400)
    return success_response(data, "Sales by category")
