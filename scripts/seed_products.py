"""Fill the products table with the bakery's fictitious inventory, queried by
the check_stock tool. Safe to re-run: existing rows are replaced."""

from app.db.client import get_client

# Kept consistent with docs/allergens.md (vegan items have no milk or eggs;
# the almond cookies and buckwheat loaf are the gluten-free options).
PRODUCTS = [
    {"name": "Country sourdough", "stock_qty": 12, "price": 8.50, "allergens": ["wheat"]},
    {"name": "Seeded rye", "stock_qty": 6, "price": 9.00, "allergens": ["wheat", "sesame"]},
    {"name": "Baguette", "stock_qty": 20, "price": 4.00, "allergens": ["wheat"]},
    {"name": "Buckwheat loaf", "stock_qty": 3, "price": 10.00, "allergens": []},
    {"name": "Butter croissant", "stock_qty": 18, "price": 3.75, "allergens": ["wheat", "milk", "eggs"]},
    {"name": "Cinnamon roll", "stock_qty": 0, "price": 4.25, "allergens": ["wheat", "milk", "eggs"]},
    {"name": "Almond flour cookies", "stock_qty": 24, "price": 2.50, "allergens": ["tree nuts", "eggs"]},
    {"name": "Oat and raisin cookies", "stock_qty": 15, "price": 2.25, "allergens": ["wheat", "soy"]},
    {"name": "Walnut banana bread", "stock_qty": 4, "price": 7.50, "allergens": ["wheat", "milk", "eggs", "tree nuts"]},
]


def seed() -> None:
    client = get_client()
    # supabase-py refuses an unfiltered delete, so match every row explicitly.
    client.table("products").delete().gte("id", 0).execute()
    client.table("products").insert(PRODUCTS).execute()
    print(f"Seeded {len(PRODUCTS)} products.")


if __name__ == "__main__":
    seed()
