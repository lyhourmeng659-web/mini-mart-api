from datetime import datetime, timezone, timedelta

from app.repositories.order_repository import OrderRepository


class ReportService:
    @staticmethod
    def _parse_period(period: str):
        now = datetime.now(timezone.utc)
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "weekly":
            start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            start, end = None, None
        return start, end

    @staticmethod
    def _resolve_date_range(period, start_date, end_date):
        """Parse custom dates or fall back to period-based range."""
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
                end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
                return start, end, None
            except ValueError:
                return None, None, "Invalid date format. Use YYYY-MM-DD"
        start, end = ReportService._parse_period(period)
        return start, end, None

    @staticmethod
    def sales_summary(period="daily", start_date=None, end_date=None):
        start, end, err = ReportService._resolve_date_range(
            period, start_date, end_date
        )
        if err:
            return None, err

        rows = OrderRepository.sales_by_period(start, end)
        data = [
            {
                "date": str(r.date),
                "order_count": r.order_count,
                "revenue": float(r.revenue or 0),
            }
            for r in rows
        ]
        total_revenue = sum(d["revenue"] for d in data)
        total_orders = sum(d["order_count"] for d in data)
        return {
            "period": period,
            "from": start.isoformat() if start else start_date,
            "to": end.isoformat() if end else end_date,
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "breakdown": data,
        }, None

    @staticmethod
    def sales_by_product(period="monthly", start_date=None, end_date=None):
        start, end, err = ReportService._resolve_date_range(
            period, start_date, end_date
        )
        if err:
            return None, err

        rows = OrderRepository.sales_by_product(start, end)
        return [
            {
                "product_id": r.id,
                "product_name": r.name,
                "total_qty_sold": int(r.total_qty or 0),
                "revenue": float(r.revenue or 0),
            }
            for r in rows
        ], None

    @staticmethod
    def sales_by_category(period="monthly", start_date=None, end_date=None):
        start, end, err = ReportService._resolve_date_range(
            period, start_date, end_date
        )
        if err:
            return None, err

        rows = OrderRepository.sales_by_category(start, end)
        return [
            {
                "category_id": r.id,
                "category_name": r.name,
                "total_qty_sold": int(r.total_qty or 0),
                "revenue": float(r.revenue or 0),
            }
            for r in rows
        ], None
