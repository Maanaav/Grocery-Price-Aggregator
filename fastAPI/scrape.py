"""⚠️ DISCLAIMER: This script is intended for educational and research purposes only. It is NOT affiliated with,
endorsed by, or authorized by Woolworths, Coles, or IGA. Use of this script may violate the Terms of Service of these
websites, and automated scraping or unauthorized API requests can result in account bans, legal consequences,
or IP blocking. By using this code, you acknowledge that you are solely responsible for your actions and agree not to
use it for any illegal or unethical activities. The author assumes no liability for misuse of this script."""

from datetime import datetime
import requests
from bs4 import BeautifulSoup


def search_woolworths_api(search_term, session_cookie):
    """
    Makes a direct POST request to Woolworths' search API.
    """

    url = "https://www.woolworths.com.au/apis/ui/Search/products"
    headers = {
        "Content-Type": "application/json",
        "Cookie": session_cookie,
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/133.0.0.0 Safari/537.36"
        ),
        "Origin": "https://www.woolworths.com.au",
        "Referer": f"https://www.woolworths.com.au/shop/search/products?searchTerm={search_term}"
    }

    payload = {
        "SearchTerm": search_term,
        "PageNumber": 1,
        "PageSize": 36,
        "SortType": "TraderRelevance",
        "Filters": [],
        "FormatObject": {
            "Name": "SearchFormat",
            "Filters": [],
            "Misc": {},
            "DisplayPreference": "List"
        }
    }

    print(f"Searching Woolworths for: {search_term}")

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f"[!] Woolworths API request failed: {resp.status_code} - {resp.text[:200]}...")
        return [{
            "store_name": "Woolworths",
            "product_name": search_term,
            "price": "Not found ERROR",
        }]

    data = resp.json()
    if "Products" not in data:
        return [{
            "store_name": "Woolworths",
            "product_name": search_term,
            "price": "Not found ERROR",
        }]

    results = []
    for product_group in data["Products"]:
        for product in product_group.get("Products", []):
            name = product.get("DisplayName", "")
            price_val = product.get("Price", 0)
            product_price = f"${price_val:.2f}" if price_val else "Not found"

            results.append({
                "store_name": "Woolworths",
                "product_name": name,
                "price": product_price,
            })

    return results[:5]


def search_coles_api(search_term, coles_cookie):
    """
    Uses a direct GET request to fetch the Coles search page, then parses HTML with BeautifulSoup.
    (May still face captchas if Coles anti-bot is strict.)
    """
    base_url = f"https://www.coles.com.au/search/products?q={search_term.replace(' ', '%20')}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": coles_cookie,
    }

    print(f"Searching Coles for: {search_term}")

    resp = requests.get(base_url, headers=headers)
    if resp.status_code != 200:
        print(f"[!] Coles request failed: {resp.status_code} - {resp.text[:200]}...")
        return [{
            "store_name": "Coles",
            "product_name": search_term,
            "price": "Not found ERROR",
        }]

    # If the response is a captcha page, you won't find the normal .product__title elements.
    soup = BeautifulSoup(resp.text, "html.parser")

    products = soup.select(".product__title")
    prices = soup.select(".price")

    # If we suspect captcha, products list might be empty or contain a "robot" message.
    if not products:
        print(" - No products found or captcha triggered.")
        return [{
            "store_name": "Coles",
            "product_name": search_term,
            "price": "Not found ERROR",
        }]

    results = []
    for product, price in zip(products, prices):
        product_name = product.get_text(strip=True)
        product_price = price.get_text(strip=True)

        results.append({
            "store_name": "Coles",
            "product_name": product_name,
            "price": product_price,
        })

    return results[:5]


def search_iga_api(search_term, iga_cookie, take=20):
    base_url = "https://www.igashop.com.au/api/storefront/stores/32600/search"

    params = {
        "q": search_term,
        "take": take,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/133.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Referer": f"https://www.igashop.com.au/search/1?q={search_term}",
        "x-shopping-mode": "11111111-1111-1111-1111-111111111111",
        "Cookie": iga_cookie,
    }

    print(f"Searching IGA for: {search_term}")
    resp = requests.get(base_url, headers=headers, params=params)

    if resp.status_code != 200:
        print(f"[!] IGA API request failed: {resp.status_code} - {resp.text[:200]}...")
        return [{
            "store_name": "IGA",
            "product_name": search_term,
            "price": "Not found ERROR",
        }]

    data = resp.json()
    items = data.get("items", [])

    results = []
    for item in items:
        product_name = item.get("name") or "Unnamed Product"
        pricing_info = item.get("price")

        unit_of_size = item.get('unitOfSize')
        if isinstance(unit_of_size, list) and unit_of_size:
            product_weight = f"{unit_of_size[0].get('size', '')} {unit_of_size[0].get('type', '')}".strip()
        elif isinstance(unit_of_size, dict):
            # If it's a dict, try to access the keys directly.
            product_weight = f"{unit_of_size.get('size', '')} {unit_of_size.get('type', '')}".strip()
        else:
            product_weight = ""

        results.append({
            "store_name": "IGA",
            "product_name": product_name + " " + product_weight,
            "price": pricing_info,
        })

    return results[:5]
