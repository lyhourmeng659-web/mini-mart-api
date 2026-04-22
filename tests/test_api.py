"""
Integration tests for Mini Mart API.
Run with: python -m pytest tests/ -v
"""
import pytest
import json
from app import create_app, db
from config import TestingConfig


@pytest.fixture(scope="module")
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        _seed_test_data(application)
        yield application
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def admin_token(client):
    r = client.post("/api/admin/auth/login",
                    json={"email": "admin@test.com", "password": "Admin@1234"})
    return r.get_json()["data"]["access_token"]


@pytest.fixture(scope="module")
def customer_token(client):
    r = client.post("/api/front/auth/login",
                    json={"email": "customer@test.com", "password": "Cust@1234"})
    return r.get_json()["data"]["access_token"]


def _seed_test_data(application):
    from app import bcrypt
    from app.models.user import User, Role
    from app.models.category import Category
    from app.models.product import Product

    admin_role = Role(name="admin")
    cust_role = Role(name="customer")
    db.session.add_all([admin_role, cust_role])
    db.session.flush()

    admin = User(
        name="Test Admin", email="admin@test.com",
        password_hash=bcrypt.generate_password_hash("Admin@1234").decode(),
        role_id=admin_role.id,
    )
    customer = User(
        name="Test Customer", email="customer@test.com",
        password_hash=bcrypt.generate_password_hash("Cust@1234").decode(),
        role_id=cust_role.id,
    )
    db.session.add_all([admin, customer])
    db.session.flush()

    cat = Category(name="Beverages", description="Drinks")
    db.session.add(cat)
    db.session.flush()

    p1 = Product(name="Cola 1L", price=1.99, stock=100, category_id=cat.id)
    p2 = Product(name="Juice 500ml", price=2.49, stock=50, category_id=cat.id)
    db.session.add_all([p1, p2])
    db.session.commit()


#  Health

class TestHealth:
    def test_health_check(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.get_json()["success"] is True


#  Auth

class TestCustomerAuth:
    def test_register_success(self, client):
        r = client.post("/api/front/auth/register", json={
            "name": "New User", "email": "new@test.com", "password": "New@12345"
        })
        d = r.get_json()
        assert r.status_code == 201
        assert d["success"] is True
        assert d["data"]["email"] == "new@test.com"

    def test_register_duplicate_email(self, client):
        r = client.post("/api/front/auth/register", json={
            "name": "Dup", "email": "customer@test.com", "password": "Dup@12345"
        })
        assert r.status_code == 400
        assert r.get_json()["success"] is False

    def test_register_invalid_password(self, client):
        r = client.post("/api/front/auth/register", json={
            "name": "Weak", "email": "weak@test.com", "password": "short"
        })
        assert r.status_code == 400

    def test_login_success(self, client):
        r = client.post("/api/front/auth/login",
                        json={"email": "customer@test.com", "password": "Cust@1234"})
        d = r.get_json()
        assert r.status_code == 200
        assert "access_token" in d["data"]
        assert "refresh_token" in d["data"]

    def test_login_wrong_password(self, client):
        r = client.post("/api/front/auth/login",
                        json={"email": "customer@test.com", "password": "Wrong@1234"})
        assert r.status_code == 401

    def test_get_profile(self, client, customer_token):
        r = client.get("/api/front/auth/me",
                       headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200
        assert r.get_json()["data"]["email"] == "customer@test.com"

    def test_profile_requires_auth(self, client):
        r = client.get("/api/front/auth/me")
        assert r.status_code == 401


class TestAdminAuth:
    def test_admin_login_success(self, client):
        r = client.post("/api/admin/auth/login",
                        json={"email": "admin@test.com", "password": "Admin@1234"})
        d = r.get_json()
        assert r.status_code == 200
        assert d["success"] is True

    def test_customer_cannot_use_admin_login(self, client):
        r = client.post("/api/admin/auth/login",
                        json={"email": "customer@test.com", "password": "Cust@1234"})
        assert r.status_code == 403


#  Products

class TestProducts:
    def test_list_products_public(self, client):
        r = client.get("/api/front/products")
        d = r.get_json()
        assert r.status_code == 200
        assert "items" in d["data"]
        assert "pagination" in d["data"]

    def test_list_products_paginated(self, client):
        r = client.get("/api/front/products?page=1&per_page=1")
        d = r.get_json()
        assert len(d["data"]["items"]) <= 1

    def test_search_products(self, client):
        r = client.get("/api/front/products?search=Cola")
        items = r.get_json()["data"]["items"]
        assert any("Cola" in p["name"] for p in items)

    def test_get_product_detail(self, client):
        r = client.get("/api/front/products/1")
        assert r.status_code == 200
        assert r.get_json()["data"]["id"] == 1

    def test_get_nonexistent_product(self, client):
        r = client.get("/api/front/products/99999")
        assert r.status_code == 404

    def test_admin_create_product(self, client, admin_token):
        r = client.post("/api/admin/products",
                        json={"name": "New Product", "price": 5.99,
                              "category_id": 1, "stock": 20},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 201
        assert r.get_json()["data"]["name"] == "New Product"

    def test_admin_update_product(self, client, admin_token):
        r = client.put("/api/admin/products/1",
                       json={"price": 2.49, "stock": 90},
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert float(r.get_json()["data"]["price"]) == 2.49

    def test_customer_cannot_create_product(self, client, customer_token):
        r = client.post("/api/admin/products",
                        json={"name": "Hack", "price": 0.01, "category_id": 1},
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 403


#  Categories

class TestCategories:
    def test_list_public_categories(self, client):
        r = client.get("/api/front/categories")
        assert r.status_code == 200
        items = r.get_json()["data"]
        assert isinstance(items, list)
        assert len(items) >= 1

    def test_admin_create_category(self, client, admin_token):
        r = client.post("/api/admin/categories",
                        json={"name": "Dairy", "description": "Milk products"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 201

    def test_duplicate_category_rejected(self, client, admin_token):
        r = client.post("/api/admin/categories",
                        json={"name": "Beverages"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 400

    def test_admin_update_category(self, client, admin_token):
        r = client.put("/api/admin/categories/1",
                       json={"description": "Updated description"},
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200


#  Cart

class TestCart:
    def test_view_empty_cart(self, client, customer_token):
        r = client.get("/api/front/cart",
                       headers={"Authorization": f"Bearer {customer_token}"})
        d = r.get_json()["data"]
        assert r.status_code == 200
        assert d["item_count"] == 0

    def test_add_item_to_cart(self, client, customer_token):
        r = client.post("/api/front/cart/add",
                        json={"product_id": 1, "quantity": 2},
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 201
        d = r.get_json()["data"]
        assert d["quantity"] == 2
        assert d["subtotal"] > 0

    def test_cart_requires_auth(self, client):
        r = client.get("/api/front/cart")
        assert r.status_code == 401

    def test_add_invalid_quantity(self, client, customer_token):
        r = client.post("/api/front/cart/add",
                        json={"product_id": 1, "quantity": 0},
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 400

    def test_update_cart_item(self, client, customer_token):
        r = client.put("/api/front/cart/update",
                       json={"product_id": 1, "quantity": 5},
                       headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200
        assert r.get_json()["data"]["quantity"] == 5

    def test_remove_cart_item(self, client, customer_token):
        r = client.delete("/api/front/cart/remove/1",
                          headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200

    def test_clear_cart(self, client, customer_token):
        # Add an item first
        client.post("/api/front/cart/add",
                    json={"product_id": 2, "quantity": 1},
                    headers={"Authorization": f"Bearer {customer_token}"})
        r = client.delete("/api/front/cart/clear",
                          headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200
        r2 = client.get("/api/front/cart",
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r2.get_json()["data"]["item_count"] == 0


#  Orders

class TestOrders:
    def test_checkout_empty_cart_fails(self, client, customer_token):
        r = client.post("/api/front/orders/checkout",
                        json={"shipping_address": "123 Main St"},
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 400

    def test_full_checkout_flow(self, client, customer_token, admin_token):
        # Add items
        client.post("/api/front/cart/add",
                    json={"product_id": 1, "quantity": 2},
                    headers={"Authorization": f"Bearer {customer_token}"})
        client.post("/api/front/cart/add",
                    json={"product_id": 2, "quantity": 1},
                    headers={"Authorization": f"Bearer {customer_token}"})

        # Checkout
        r = client.post("/api/front/orders/checkout",
                        json={"shipping_address": "10 Maple Ave", "notes": "Call on arrival"},
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 201
        d = r.get_json()["data"]
        assert d["status"] == "pending"
        assert d["total_amount"] > 0
        assert len(d["items"]) == 2
        assert d["order_number"].startswith("ORD-")

        order_id = d["id"]

        # Customer can view their order
        r2 = client.get(f"/api/front/orders/{order_id}",
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r2.status_code == 200

        # Admin updates status
        r3 = client.put(f"/api/admin/orders/{order_id}/status",
                        json={"status": "shipped"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r3.status_code == 200
        assert r3.get_json()["data"]["status"] == "shipped"

    def test_invalid_order_status_rejected(self, client, admin_token):
        r = client.put("/api/admin/orders/1/status",
                       json={"status": "teleported"},
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 400

    def test_customer_cannot_see_others_order(self, client, customer_token):
        # Order 99999 doesn't exist
        r = client.get("/api/front/orders/99999",
                       headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code in (403, 404)


#  Reports

class TestReports:
    def test_daily_sales(self, client, admin_token):
        r = client.get("/api/admin/reports/sales/daily",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        d = r.get_json()["data"]
        assert "total_revenue" in d
        assert "total_orders" in d

    def test_weekly_sales(self, client, admin_token):
        r = client.get("/api/admin/reports/sales/weekly",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_monthly_sales(self, client, admin_token):
        r = client.get("/api/admin/reports/sales/monthly",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_sales_by_product(self, client, admin_token):
        r = client.get("/api/admin/reports/sales/by-product",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert isinstance(r.get_json()["data"], list)

    def test_sales_by_category(self, client, admin_token):
        r = client.get("/api/admin/reports/sales/by-category",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert isinstance(r.get_json()["data"], list)

    def test_custom_date_range(self, client, admin_token):
        r = client.get("/api/admin/reports/sales?start_date=2026-01-01&end_date=2026-12-31",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_reports_require_admin(self, client, customer_token):
        r = client.get("/api/admin/reports/sales/daily",
                       headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 403
