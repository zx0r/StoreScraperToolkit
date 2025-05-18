#!/usr/bin/env python3

import re
import json
import asyncio
import aiohttp
import argparse
import logging
from pathlib import Path
from datetime import datetime
from rich.progress import Progress
from rich.logging import RichHandler

# Set up logging with rich handler for color output
logging.basicConfig(
    level=logging.DEBUG,  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(message)s",  # Just print the log message (no timestamp, log level, etc.)
    handlers=[RichHandler(rich_tracebacks=True)],  # RichHandler for pretty output
)

# Create logger
logger = logging.getLogger()

# === CONSTANTS ===
DEFAULT_CITY = "Краснодар"
DEFAULT_CATEGORY = "vino"
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20

BASE_URL = "https://alkoteka.com/web-api/v1"
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

CITY_CACHE = CACHE_DIR / "cities.json"
FILTER_CACHE = CACHE_DIR / "filters.json"
CATEGORY_CACHE = CACHE_DIR / "category.json"


# === HTTP ===
async def fetch_json(session, url, params=None):
    """Fetch JSON data from the given URL with optional parameters."""
    try:
        async with session.get(
            url, params=params, headers={"Accept": "application/json"}
        ) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch data from {url}!")
        return None


# === CACHE ===
def save_json(path, data):
    """Save data to a JSON file."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path):
    """Load data from a JSON file if it exists."""
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


# === STEP 1: CITY ===
async def get_city_uuid(session, city_name):
    """Retrieve the UUID for a given city."""
    cities = load_json(CITY_CACHE)
    if not cities:
        data = await fetch_json(session, f"{BASE_URL}/city")
        if not data:
            return None
        combined = data.get("meta", {}).get("accented", []) + data.get("results", [])
        cities = {city["name"]: city["uuid"] for city in combined}
        save_json(CITY_CACHE, cities)
    return cities.get(city_name)


# === STEP 2: FILTERS ===
async def fetch_facets(session, city_uuid):
    """Fetch facets for filtering products."""
    return await fetch_json(
        session,
        f"{BASE_URL}/product",
        {
            "city_uuid": city_uuid,
            "page": 1,
            "per_page": 100,
        },
    )


def extract_filters(facets):
    """Extract filters from facet data."""
    filters = {}
    for facet in facets:
        code = facet.get("code")
        values = facet.get("values", [])
        if code and values:
            filters[code] = [
                {"name": val["name"], "slug": val["slug"]}
                for val in values
                if val.get("enabled")
            ]
    return filters


async def update_filter_cache(session, city_uuid):
    """Update the filter and category caches."""
    facets = (await fetch_facets(session, city_uuid)).get("meta", {}).get("facets", [])
    filters = extract_filters(facets)

    products = await fetch_products(
        session, city_uuid, category=None, page=1, per_page=1000, filters={}
    )
    categories = {
        p["category"]["slug"]: p["category"] for p in products if "category" in p
    }

    save_json(FILTER_CACHE, filters)
    save_json(CATEGORY_CACHE, categories)
    logger.info("Filters and categories updated")


# === STEP 3: PRODUCTS ===
async def fetch_products(
    session, city_uuid, category=None, page=1, per_page=50, filters=None
):
    """Fetch products based on filters and pagination."""
    params = {
        "city_uuid": city_uuid,
        "page": page,
        "per_page": per_page,
    }
    if category:
        params["root_category_slug"] = category
    if filters:
        for code, values in filters.items():
            for val in values:
                key = f"options[{code}][]"
                params.setdefault(key, []).append(val)

    data = await fetch_json(session, f"{BASE_URL}/product", params=params)
    return data.get("results", []) if data else []


def sanitize_filename_component(value):
    """Sanitize a string to create a valid filename component."""
    return re.sub(r"[^\w\-]", "_", value.strip().lower())


# === STEP 4: DISPLAY ===
def display_product(product):
    """Display product details."""
    print(f"🛒 UUID: {product.get('uuid', 'N/A')}")
    print(f"🛒 Name: {product.get('name', 'N/A')}")
    print(f"🛒 SubName: {product.get('subname', 'N/A')}")
    print(
        f"🧷 Каталог: {product.get('category', {}).get('parent', {}).get('name', 'Без категории')}"
    )
    print(
        f"🧷 Категория: {product.get('category', {}).get('name', 'Без подкатегории')}"
    )

    sugar = color = volume = "N/A"
    for label in product.get("filter_labels", []):
        f = label.get("filter")
        title = label.get("title", "")
        if f == "cvet":
            color = title
        elif f == "soderzanie-saxara":
            sugar = title
        elif f == "obem":
            volume = title

    print(f"🎨 Цвет: {color}")
    print(f"🍬 Сахар: {sugar}")
    print(f"🍾 Объём: {volume}")
    print(f"💰 Цена: {product.get('price', 'N/A')} ₽")
    print(f"🌐 Ссылка: {product.get('product_url', '')}")
    print(f"🖼️ Изображение: {product.get('image_url', '')}")
    print("-" * 60)


# === SAVE PRODUCTS ===
def save_products(
    products: list[dict[str, object]], path: Path | str = Path("products.ndjson")
) -> None:
    path = Path(path)  # Преобразуем строку в Path, если нужно
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for product in products:
            f.write(json.dumps(product, ensure_ascii=False) + "\n")

    logger.info(f"Saved {len(products)} products to {path}")


# === CLI ENTRYPOINT ===
def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Alkoteka.com scraper")
    parser.add_argument("--city", default=DEFAULT_CITY)
    parser.add_argument("--category", default=DEFAULT_CATEGORY)
    parser.add_argument("--color", nargs="*", help="Color slugs")
    parser.add_argument("--sugar", nargs="*", help="Sugar slugs")
    parser.add_argument("--page", type=int, default=DEFAULT_PAGE)
    parser.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)
    parser.add_argument(
        "--refresh-meta", action="store_true", help="Refresh filter cache"
    )
    parser.add_argument(
        "--fetch-all", action="store_true", help="Fetch all products across all pages"
    )
    return parser.parse_args()


# MAIN
async def main():
    """Main function to fetch and save products."""
    args = parse_arguments()

    async with aiohttp.ClientSession() as session:
        city_uuid = await get_city_uuid(session, args.city)
        if not city_uuid:
            logger.error("City UUID not found.")
            return

        if args.refresh_meta or not FILTER_CACHE.exists():
            await update_filter_cache(session, city_uuid)

        filters = {}
        if args.color:
            filters["cvet"] = args.color
        if args.sugar:
            filters["soderzanie-saxara"] = args.sugar

        products = []

        timestamp = datetime.now().strftime("%Y%m%d")
        parts = ["alkoteka", sanitize_filename_component(args.category)]
        if args.color:
            parts.extend([sanitize_filename_component(c) for c in args.color])
        if args.sugar:
            parts.extend([sanitize_filename_component(s) for s in args.sugar])
        if args.fetch_all:
            parts.append("all")

        parts.append(timestamp)
        filename = "_".join(parts) + ".ndjson"

        if args.fetch_all:
            logger.info(f"Fetching all products...")
            page = 1

            with Progress() as progress:
                task = progress.add_task("[cyan]Fetching pages...", total=None)

                while True:
                    result = await fetch_products(
                        session, city_uuid, args.category, page, args.per_page, filters
                    )
                    if not result:
                        break
                    products.extend(result)
                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Page {page} ({len(result)} items)",
                    )
                    page += 1

                progress.update(task, completed=page - 1)
        else:
            result = await fetch_products(
                session, city_uuid, args.category, args.page, args.per_page, filters
            )
            if result:
                products.extend(result)

        if not products:
            logger.error("No products found!")
            return

        for product in products:
            display_product(product)

        # Save the products to a file
        save_products(products, filename)

        # NDJSON
        # import pandas as pd

        # file_path = "result/alkoteka_vino_all_20250518.ndjson"
        # df = pd.read_json(file_path, lines=True)


if __name__ == "__main__":
    asyncio.run(main())
