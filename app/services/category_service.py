from app.repositories.category_repository import CategoryRepository


class CategoryService:
    @staticmethod
    def get_all(page=1, per_page=10, active_only=False):
        pagination = CategoryRepository.get_all(page=page, per_page=per_page, active_only=active_only)
        return pagination.items, pagination.total

    @staticmethod
    def get_all_active():
        return CategoryRepository.get_all_active(), None

    @staticmethod
    def get_by_id(category_id: int):
        cat = CategoryRepository.find_by_id(category_id)
        if cat is None:
            return None, "Category not found"
        return cat, None

    @staticmethod
    def create(name: str, description: str = None):
        if not name:
            return None, "Category name is required"
        if CategoryRepository.find_by_name(name):
            return None, "Category already exists"

        cat = CategoryRepository.create(name=name, description=description)
        return cat, None

    @staticmethod
    def update(category_id: int, **kwargs):
        cat = CategoryRepository.find_by_id(category_id)
        if not cat:
            return None, "Category not found"
        if "name" in kwargs and kwargs["name"] != cat.name:
            if CategoryRepository.find_by_name(kwargs["name"]):
                return None, "Category name already in use"

        CategoryRepository.update(cat, **kwargs)
        return cat, None

    @staticmethod
    def delete(category_id: int):
        cat = CategoryRepository.find_by_id(category_id)
        if not cat:
            return False, "Category not found"
        if cat.products:
            return False, "Category already contains products"
        CategoryRepository.delete(cat)
        return True, None
