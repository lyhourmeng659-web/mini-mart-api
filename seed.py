"""
Seed script — run once to populate the database with initial data.

Usage:
    python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from run import app
from app import db, bcrypt
from app.models.user import User, Role
from app.models.category import Category
from app.models.product import Product


def seed():
    with app.app_context():
        print("🌱  Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()

        #  Roles
        admin_role = Role(name="admin")
        customer_role = Role(name="customer")
        db.session.add_all([admin_role, customer_role])
        db.session.flush()

        #  Users
        admin = User(
            name="Super Admin",
            email="admin@minimart.com",
            password_hash=bcrypt.generate_password_hash("Admin@1234").decode("utf-8"),
            role_id=admin_role.id,
            phone="+1-000-000-0000",
            address="123 Admin Street, HQ",
        )
        customer1 = User(
            name="Alice Johnson",
            email="alice@example.com",
            password_hash=bcrypt.generate_password_hash("Alice@1234").decode("utf-8"),
            role_id=customer_role.id,
            phone="+1-555-100-0001",
            address="10 Maple Avenue, Springfield",
        )
        customer2 = User(
            name="Bob Smith",
            email="bob@example.com",
            password_hash=bcrypt.generate_password_hash("Bob@12345").decode("utf-8"),
            role_id=customer_role.id,
            phone="+1-555-100-0002",
            address="20 Oak Lane, Shelbyville",
        )
        db.session.add_all([admin, customer1, customer2])
        db.session.flush()

        #  Categories
        categories_data = [
            ("Beverages", "Drinks, juices, water, coffee, and tea"),
            ("Snacks", "Chips, biscuits, crackers, and light bites"),
            ("Dairy", "Milk, cheese, butter, and yogurt products"),
            ("Bakery", "Bread, cakes, pastries, and baked goods"),
            ("Frozen Foods", "Frozen meals, ice cream, and frozen vegetables"),
            ("Personal Care", "Soap, shampoo, dental care, and hygiene products"),
            ("Household", "Cleaning supplies and home essentials"),
            ("Produce", "Fresh fruits and vegetables"),
        ]
        categories = {}
        for name, desc in categories_data:
            cat = Category(name=name, description=desc)
            db.session.add(cat)
            categories[name] = cat
        db.session.flush()

        #  Products
        products_data = [
            # Beverages
            ("Coca-Cola 1.5L", "Refreshing cola drink", 1.99, 150, "Beverages"),
            ("Orange Juice 1L", "100% fresh squeezed orange juice", 3.49, 80, "Beverages"),
            ("Mineral Water 500ml", "Pure natural mineral water", 0.99, 300, "Beverages"),
            ("Green Tea (25 bags)", "Premium Japanese green tea", 4.99, 60, "Beverages"),
            ("Energy Drink 250ml", "Boost energy drink", 2.49, 120, "Beverages"),
            # Snacks
            ("Potato Chips 200g", "Classic salted potato chips", 2.29, 200, "Snacks"),
            ("Chocolate Cookies 300g", "Rich chocolate sandwich cookies", 3.19, 90, "Snacks"),
            ("Mixed Nuts 250g", "Roasted assorted nuts", 5.99, 45, "Snacks"),
            ("Popcorn 100g", "Microwave buttered popcorn", 1.79, 110, "Snacks"),
            # Dairy
            ("Full Cream Milk 1L", "Fresh pasteurized full cream milk", 1.89, 100, "Dairy"),
            ("Cheddar Cheese 200g", "Mild cheddar cheese block", 4.29, 55, "Dairy"),
            ("Greek Yogurt 500g", "Thick and creamy plain Greek yogurt", 3.79, 70, "Dairy"),
            ("Butter 250g", "Unsalted premium butter", 2.99, 85, "Dairy"),
            # Bakery
            ("White Bread 500g", "Soft sliced white bread", 2.19, 60, "Bakery"),
            ("Croissants 6-pack", "Buttery flaky croissants", 4.49, 40, "Bakery"),
            ("Chocolate Muffins 4-pack", "Double chocolate chip muffins", 3.99, 35, "Bakery"),
            # Frozen Foods
            ("Frozen Pizza 400g", "Classic Margherita frozen pizza", 5.49, 50, "Frozen Foods"),
            ("Vanilla Ice Cream 1L", "Creamy vanilla bean ice cream", 4.99, 65, "Frozen Foods"),
            ("Frozen Mixed Veg 500g", "Peas, carrots, corn, and beans", 2.49, 90, "Frozen Foods"),
            # Personal Care
            ("Shampoo 400ml", "Moisturizing shampoo for all hair types", 6.99, 75, "Personal Care"),
            ("Body Wash 500ml", "Refreshing citrus body wash", 5.49, 80, "Personal Care"),
            ("Toothpaste 150g", "Whitening fluoride toothpaste", 3.29, 100, "Personal Care"),
            # Household
            ("Dish Soap 750ml", "Grease-cutting dish washing liquid", 2.99, 95, "Household"),
            ("Laundry Detergent 1kg", "Powerful stain remover powder", 7.99, 55, "Household"),
            # Produce
            ("Bananas 1kg", "Fresh ripe bananas", 1.49, 120, "Produce"),
            ("Tomatoes 500g", "Vine-ripened tomatoes", 2.19, 90, "Produce"),
            ("Baby Spinach 200g", "Tender baby spinach leaves", 2.79, 60, "Produce"),
        ]

        for name, desc, price, stock, cat_name in products_data:
            product = Product(
                name=name,
                description=desc,
                price=price,
                stock=stock,
                category_id=categories[cat_name].id,
            )
            db.session.add(product)

        db.session.commit()

        print("✅  Seed complete!")
        print("\n📋  Credentials:")
        print("   Admin  → admin@minimart.com   / Admin@1234")
        print("   Alice  → alice@example.com    / Alice@1234")
        print("   Bob    → bob@example.com      / Bob@12345")
        print(f"\n   Categories : {len(categories_data)}")
        print(f"   Products   : {len(products_data)}")
        print(f"   Users      : 3 (1 admin, 2 customers)\n")


if __name__ == "__main__":
    seed()
