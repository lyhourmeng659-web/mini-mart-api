from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.utils.file_handler import save_image, delete_image


class ProductService:
    @staticmethod
    def get_all(page=1, per_page=10, category_id=None, search=None, active_only=False):
        pagination = ProductRepository.get_all(
            page=page, per_page=per_page, category_id=category_id,
            search=search, active_only=active_only
        )
        return pagination.items, pagination.total

    @staticmethod
    def get_by_id(product_id: int):
        product = ProductRepository.find_by_id(product_id)
        if not product:
            return None, "Product not found"
        return product, None

    @staticmethod
    def create(name, price, category_id, description=None, stock=0, image_file=None):
        if not name or price is None:
            return None, "Name and price are required"
        try:
            price = float(price)
            stock = int(stock)
        except (ValueError, TypeError):
            return None, "Invalid price or stock value"
        if price < 0:
            return None, "Price must be non-negative"
        if not CategoryRepository.find_by_id(category_id):
            return None, "Category not found"

        image_filename = None
        if image_file:
            try:
                image_filename = save_image(image_file)
            except ValueError as e:
                return None, str(e)

        product = ProductRepository.create(
            name=name, price=price, category_id=category_id,
            description=description, stock=stock, image=image_filename
        )
        return product, None

    @staticmethod
    def update(product_id: int, image_file=None, **kwargs):
        product = ProductRepository.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        if "category_id" in kwargs and kwargs["category_id"]:
            if not CategoryRepository.find_by_id(kwargs["category_id"]):
                return None, "Category not found"

        if image_file:
            try:
                old_image = product.image
                kwargs["image"] = save_image(image_file)
                if old_image:
                    delete_image(old_image)
            except ValueError as e:
                return None, str(e)

        if "price" in kwargs and kwargs["price"] is not None:
            try:
                kwargs["price"] = float(kwargs["price"])
            except (ValueError, TypeError):
                return None, "Invalid price"

        if "stock" in kwargs and kwargs["stock"] is not None:
            try:
                kwargs["stock"] = int(kwargs["stock"])
            except (ValueError, TypeError):
                return None, "Invalid stock value"

        if "is_active" in kwargs and kwargs["is_active"] is not None:
            val = kwargs["is_active"]
            if isinstance(val, str):
                kwargs["is_active"] = val.lower() == "true"

        kwargs = {
            k: v for k, v in kwargs.items() if v is not None
        }

        ProductRepository.update(product, **kwargs)
        return product, None

    @staticmethod
    def delete(product_id: int):
        product = ProductRepository.find_by_id(product_id)
        if not product:
            return False, "Product not found"
        if product.image:
            delete_image(product.image)
        ProductRepository.delete(product)
        return True, None
