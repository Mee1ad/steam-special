import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from lxml import html
import contextlib

profit = 300.00


def steam_games(request):
    url = "https://store.steampowered.com/api/featuredcategories"
    params = {
        "cc": "TR",
        "l": "en",
        "v": "1",
        "tag": "specials"
    }
    response = requests.get(url=url, params=params)
    games = []
    lira_sign = "₺"
    if response.status_code == 200:
        for game in response.json()["specials"]["items"]:
            games.append({
                "id": game["id"],
                "name": game["name"],
                "image": game["header_image"],
                "dicounted": game["discounted"],
                "discount_expiration": game["discount_expiration"],
                "original_price": game['original_price'],
                "original_price2": f"{lira_sign}{game['original_price'] / 100:.2f}",
                "discount_percent": game["discount_percent"],
                "final_price": f"{lira_sign}{game['final_price'] / 100:.2f}",
            })
    return JsonResponse({"games": games})


def rial_to_toman(price: str) -> float:
    lira_to_rial_price_str = price.replace(',', '')[:-1]
    return float(lira_to_rial_price_str) + profit


def get_lira_base_price() -> str:
    tgju_lira_page = "https://www.tgju.org/profile/price_try"
    response = requests.get(url=tgju_lira_page)
    tree = html.fromstring(response.content)
    lira_to_rial_price_obj = tree.xpath('//*[@id="main"]/div[1]/div[1]/div[1]/div/div[2]/div/h3[1]/span[2]/span[1]')
    lira_to_rial_price_str = lira_to_rial_price_obj[0].text_content().strip()
    return lira_to_rial_price_str


def lira_to_rial(price: str, lira_to_rial_price_str: str) -> str:
    lira_to_rial_price = rial_to_toman(lira_to_rial_price_str)
    price = float(price.replace('TL', '').replace('\n', '').replace('.', '').replace(',', '.'))
    final_price = price * lira_to_rial_price
    round_price = round(final_price / 1000) * 1000
    formatted_price = format(round_price, ',')
    return f"{formatted_price} Toman"


def scrape_games(request):
    page = request.GET.get('page')
    url = 'https://store.steampowered.com/search/results'
    params = {
        'supportedlang': 'english%2Cpersian',
        'specials': '1',
        'ndl': '1',
        'page': page,
    }
    lira_base_price = get_lira_base_price()
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    search_results = soup.find_all('a', class_='search_result_row')
    games = []
    for result in search_results:
        prices = result.find('div', class_='search_price').text.split(' ')
        lira_price = "0"
        price = "0"
        discounted_price = "0"
        lira_discounted_price = "0"
        discount_percent = "0"
        if len(prices) > 1:
            with contextlib.suppress(ValueError):
                price = lira_to_rial(prices[0], lira_base_price)
            lira_price = f"₺{prices[0]}"
            with contextlib.suppress(ValueError):
                discounted_price = lira_to_rial(prices[1], lira_base_price)
            lira_discounted_price = prices[1].replace('TL', '₺')
            discount_percent = result.find('div', class_='search_discount').text.replace('-', '')
        image = result.find('img')['src']
        games.append({
            "name": result.find('span', class_='title').text,
            "image": image.replace('capsule_sm_120', 'library_600x900'),
            "price": price,
            "lira_price": "".join(lira_price.split()),
            "discounted_price": discounted_price,
            "lira_discounted_price": lira_discounted_price,
            "discount_percent": "".join(discount_percent.split()),
            "steam_url": result['href'],
        })
    return JsonResponse({"games": games})


def index(request):
    return JsonResponse({"message": "Hello World"})
