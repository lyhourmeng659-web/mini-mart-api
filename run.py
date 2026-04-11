import os
from app import create_app, db
from app.models import User, Role, Category, Product, Cart, Order, OrderItem

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Role": Role,
        "Category": Category,
        "Product": Product,
        "Cart": Cart,
        "Order": Order,
        "OrderItem": OrderItem,
    }


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
