### 🛠️ Alkoteka Product Scraper – One-File CLI Tool

A fully asynchronous, CLI-driven Python tool for scraping product listings from the Alkoteka marketplace using their official public API. Built for speed, resilience, and integration-ready output.

🚀 Usage

> python alkoteka_scraper.py --city Краснодар --category vino --fetch-all --refresh-meta

⚙️ Technical Features

- Fully Async Pipeline: Non-blocking HTTP requests via aiohttp, powered by asyncio.gather for parallel fetches.
- Smart Caching: Locally caches cities, categories, and filters to reduce redundant calls.
- Dynamic Metadata Sync: Auto-refreshes categories and filter metadata with --refresh-meta.
- City UUID Resolver: Transparent city-to-UUID mapping with caching.
- Rich Logging: Console and debug logs for transparency and troubleshooting.
- Extensible CLI Interface: Built with argparse for clean automation and integration.
- Streamable Output Format: Outputs results in newline-delimited JSON (NDJSON).


🧱 Stack & Technologies

| Purpose             | Tool/Lib          |
| ------------------- | ----------------- |
| Language            | Python 3.12+      |
| HTTP Client         | aiohttp           |
| CLI Args            | argparse          |
| Async Orchestration | asyncio           |
| Caching & I/O       | pathlib, json     |
| Data Analysis       | pandas (optional) |


⚠️ Comparison: API vs Scrapy-Based Parsing

| Feature                    | Alkoteka Product Fetcher (API)         | Scrapy-Based HTML Parsing              |
| -------------------------- | -------------------------------------- | -------------------------------------- |
| Method                     | REST API Integration                   | HTML Parsing (XPath/CSS)               |
| Reliability                | High – structured server response      | Medium – depends on DOM structure      |
| Speed                      | Fast – no parsing overhead             | Slower – DOM traversal required        |
| Resilience to Site Changes | Stable – backend rarely changes        | Fragile – frontend changes break logic |
| Legal Risks                | Minimal – using official API           | Possible – may breach ToS              |
| Caching                    | Built-in (cities, filters, categories) | Manual implementation required         |
| Setup Complexity           | Low – single script + pip install      | Moderate – Scrapy project layout       |
| CLI/Script Integration     | Excellent – argparse compatible        | Requires additional wrappers           |
| CI/CD & Automation         | Easy to integrate                      | Needs configuration adjustments        |:
| Scalability                | Great for lightweight workflows        | Suited for large crawls/spiders        |

📁 Project Structure

```bash
alkoteka_scraper.py         # Main scraper script (entry point)
├── cache/
│   ├── cities.json         # Cached UUIDs for cities
│   ├── filters.json        # Cached filters per category
│   └── categories.json     # Cached available categories
├── results/
    └── alkoteka_{slug}.ndjson  # Output file (1 JSON per line)
```

📦 Sample Output Record

```text
🛒 UUID: 016e998b-cd04-11eb-80cf-00155d03900a
🛒 Name: Бельбек Розе Каберне Совиньон
🛒 SubName: None
🧷 Каталог: Вино
🧷 Категория: Вино тихое
🎨 Цвет: Розовое
🍬 Сахар: Сухое
🍾 Объём: 0.75 Л
💰 Цена: 1330 ₽
🌐 Ссылка: https://alkoteka.com/product/vino-tikhoe/belbek-roze-kaberne-sovinon_55714
🖼️ Изображение: https://web.alkoteka.com/resize/350_500/product/fd/54/55714_image.png
------------------------------------------------------------
🛒 UUID: 1ec5f71d-09eb-11ea-8100-00155d2fc707
🛒 Name: Шапийон Сьендра
🛒 SubName: Chapillon Siendra
🧷 Каталог: Вино
🧷 Категория: Вино тихое
🎨 Цвет: Красное
🍬 Сахар: Сухое
🍾 Объём: 0.75 Л
💰 Цена: 1995 ₽
🌐 Ссылка: https://alkoteka.com/product/vino-tikhoe/shapiyon-sendra_45707
🖼️ Изображение: https://web.alkoteka.com/resize/350_500/product/8b/fc/45707_image.png
------------------------------------------------------------
🛒 UUID: 30ec359d-b94c-11eb-80ce-00155d03900a
🛒 Name: Джулиана Вичини Треббьяно д`Абруццо
🛒 SubName: Giuliana Vicini Trebbiano d’Abruzzo
🧷 Каталог: Вино
🧷 Категория: Вино тихое
🎨 Цвет: Белое
🍬 Сахар: Сухое
🍾 Объём: 0.75 Л
💰 Цена: 1495 ₽
🌐 Ссылка: https://alkoteka.com/product/vino-tikhoe/dzhuliana-vichini-trebbyano-d-abrucco_55292
🖼️ Изображение: https://web.alkoteka.com/resize/350_500/product/ef/d1/55292_image.png
------------------------------------------------------------
🛒 UUID: 390ade6f-73fc-11ea-8102-00155d05c408
🛒 Name: Януб Бьянко
🛒 SubName: Janub Bianco
🧷 Каталог: Вино
🧷 Категория: Вино тихое
🎨 Цвет: Белое
🍬 Сахар: Полусухое
🍾 Объём: 0.75 Л
💰 Цена: 1225 ₽
🌐 Ссылка: https://alkoteka.com/product/vino-tikhoe/yanub-byanko_48086
🖼️ Изображение: https://web.alkoteka.com/resize/350_500/product/b3/72/48086_image.png
------------------------------------------------------------
🛒 UUID: 56062eee-b705-11ec-ba4e-3cecef676e4f
🛒 Name: Бамбак Розе
🛒 SubName: Bambak Rose
🧷 Каталог: Вино
🧷 Категория: Вино тихое
🎨 Цвет: Розовое
🍬 Сахар: Сухое
🍾 Объём: 0.75 Л
💰 Цена: 1490 ₽
🌐 Ссылка: https://alkoteka.com/product/vino-tikhoe/bambak-roze_63433
🖼️ Изображение: https://web.alkoteka.com/resize/350_500/product/14/25/63433_image.png
------------------------------------------------------------
```
📊 Data Analysis with Pandas

```python
import os
import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

# Loading data from NDJSON
file_path = 'result/alkoteka_vino_all_20250518.ndjson'
df = pd.read_json(file_path, lines=True)

# General information
print("Dimensions:", df.shape)
print("Columns:", df.columns.tolist())
print("Data types:\n", df.dtypes)
print("First rows:\n", df.head(3))
print("Last rows:\n", df.tail(3))

# Checking for missing values
print("Gaps:\n", df.isnull().sum())

# Statistics on numeric columns
print("Statistics:\n", df.describe())
```

```text
Dimension: (1019, 25)
Columns: ['uuid', 'name', 'slug', 'category_slug', 'rate', 'vendor_code', 'subname', 'new', 'recomended', 'price', 'prev_price', 'status', 'quantity_total', 'axioma', 'enogram', 'has_online_price', 'quantity', 'favorite', 'image_url', 'product_url', 'action_labels', 'filter_labels', 'available', 'warning', 'category']

Data types: 
uuid                 object
name                 object
slug                 object
category_slug        object
rate                float64
vendor_code           int64
subname              object
new                    bool
recomended             bool
price                 int64
prev_price          float64
status               object
quantity_total        int64
axioma                 bool
enogram                bool
has_online_price       bool
quantity              int64
favorite               bool
image_url            object
product_url          object
action_labels        object
filter_labels        object
available              bool
warning              object
category             object
dtype: object

                                    uuid                                 name  \
0  016e998b-cd04-11eb-80cf-00155d03900a        Бельбек Розе Каберне Совиньон   
1  1ec5f71d-09eb-11ea-8100-00155d2fc707                      Шапийон Сьендра   
2  30ec359d-b94c-11eb-80ce-00155d03900a  Джулиана Вичини Треббьяно д`Абруццо   

                                          slug category_slug  rate  \
0            belbek-roze-kaberne-sovinon_55714   vino-tikhoe   NaN   
1                        shapiyon-sendra_45707   vino-tikhoe   NaN   
2  dzhuliana-vichini-trebbyano-d-abrucco_55292   vino-tikhoe   NaN   

   vendor_code                              subname    new  recomended  price  \
0        55714                                 None  False        True   1330   
1        45707                    Chapillon Siendra  False        True   1995   
2        55292  Giuliana Vicini Trebbiano d’Abruzzo  False        True   1495  
```
