"""The three tools the agent can call. Each docstring is the description
Gemini reads when deciding which tool fits a question, so keep them precise."""

from langchain_core.tools import tool

from app.db.client import get_client
from app.rag.search import search

HANDOFF_MESSAGE = (
    "I've passed your conversation to a member of our team. "
    "Someone will reply to you here as soon as possible."
)


@tool
def search_knowledge(question: str) -> str:
    """Search the bakery's documents for policies and general information:
    opening hours, location, shipping, returns and refunds, allergens and
    cross-contact, custom orders, and frequently asked questions. Does NOT
    contain live stock levels or current prices."""
    results = search(question, k=3)
    return "\n\n".join(f"[source: {r['source_document']}]\n{r['content']}" for r in results)


@tool
def check_stock(product_name: str) -> str:
    """Look up a specific product in live inventory: how many are in stock
    right now, its price, and its allergens. Use the product's name, for
    example "baguette" or "croissant"."""
    # Strip LIKE wildcards so customer input can only match as plain text.
    name = product_name.strip().translate(str.maketrans("", "", "%_*"))
    rows = (
        get_client()
        .table("products")
        .select("name, stock_qty, price, allergens")
        .ilike("name", f"%{name}%")
        .limit(5)
        .execute()
        .data
    )
    if not rows:
        return f"No product matching '{name}' was found in inventory."
    return "\n".join(
        f"{r['name']}: {r['stock_qty']} in stock, ${r['price']}, "
        f"allergens: {', '.join(r['allergens']) or 'none listed'}"
        for r in rows
    )


@tool
def handoff_to_human(reason: str) -> str:
    """Escalate the conversation to a human team member. Use when the customer
    asks for a person, has a problem with a specific existing order (damaged,
    missing, wrong, or a refund to process), or needs something the other
    tools cannot answer."""
    return HANDOFF_MESSAGE


TOOLS = [search_knowledge, check_stock, handoff_to_human]
