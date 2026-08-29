def search_products(catalog: list[dict], query: str) -> list[dict]:
    return [item for item in catalog if query.lower() in item["name"].lower()]


def best_match(catalog: list[dict], query: str) -> dict:
    """Assumes search always returns at least one result."""
    results = search_products(catalog, query)
    return results[0]
