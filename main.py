import time
import requests

from _cars import create_cars_bot_message
from _wheels import create_wheels_bot_message
from _utils import get_website_config, create_urls,send_telegram_message, console
from _secrets import BOT_TOKEN, CHAT_ID1, CHAT_ID2, CHAT_ID3

# Constants
SLEEP_TIME = 60
LIMIT = 100
CONFIG_SOURCE1 = "cars-2dehands"
CONFIG_SOURCE2 = "cars-marktplaats"

CONFIG_PRICE1_2 = 500000

CONFIG_SOURCE3 = "wheels-marktplaats"
CONFIG_SOURCE4 = "wheels-2dehands"

CONFIG_PRICE3_4 = 50000

allowed_models =['audi', 'volkswagen', 'seat', 'skoda', 'bmw', 'mini', 'lexus']
CONFIG_PRICE5 = 900000

def filter_ads1(ads: list, max_price: int, newest_car_id: str = None) -> list:

    filtered_ads = [
        ad for ad in ads
        if ad["priceInfo"]["priceCents"] <= max_price and (newest_car_id is None or ad["itemId"] > newest_car_id)
    ]
    sorted_cars = sorted(filtered_ads, key=lambda x: int(x["itemId"][1:]), reverse=True)

    if not sorted_cars:
        return newest_car_id, list()
    
    # dont send cars from first iteration
    if not newest_car_id:
        return sorted_cars[0]["itemId"], list()
    
    newest_car_id = sorted_cars[0]["itemId"]
    console.print(f"Newest id: {newest_car_id}")
    return newest_car_id, sorted_cars

def filter_ads2(ads: list, max_price: int, newest_car_id: str = None) -> list:

    filtered_ads = []
    for ad in ads:
        if ad["priceInfo"]["priceCents"] <= max_price and (newest_car_id is None or ad["itemId"] > newest_car_id):
            model= ad["vipUrl"].split("/")[3]
            if model in allowed_models:
                filtered_ads.append(ad)

    sorted_cars = sorted(filtered_ads, key=lambda x: int(x["itemId"][1:]), reverse=True)

    if not sorted_cars:
        return newest_car_id, list()
    
    # dont send cars from first iteration
    if not newest_car_id:
        return sorted_cars[0]["itemId"], list()
        
    newest_car_id = sorted_cars[0]["itemId"]
    console.print(f"Newest id: {newest_car_id}")
    return newest_car_id, sorted_cars


def check_ads(config: dict, filtered_ads: list, chat_id: str, function_for_message):
    try:
        for car in filtered_ads:
            bot_message = function_for_message(car, config)
            send_telegram_message(BOT_TOKEN, chat_id, bot_message)

    except Exception as e:
        console.log(f"Error fetching data: {e}")
        send_telegram_message(BOT_TOKEN, chat_id, f"Error fetching data. Check logs for more info. {e}")
        
def main():
    config1 = get_website_config(CONFIG_SOURCE1)
    config2 = get_website_config(CONFIG_SOURCE2)
    config3 = get_website_config(CONFIG_SOURCE3)
    config4 = get_website_config(CONFIG_SOURCE4)

    urls1 = create_urls(config=config1, url_number=30, limit=LIMIT)
    urls2 = create_urls(config=config2, url_number=30, limit=LIMIT)
    urls3 = create_urls(config=config3, url_number=2, limit=LIMIT)
    urls4 = create_urls(config=config4, url_number=2, limit=LIMIT)

    newest_car_id_1 = None
    newest_car_id_2 = None
    newest_car_id_3 = None
    newest_car_id_4 = None
    newest_wheel_id_1 = None
    newest_wheel_id_2 = None

    while True:
        cars1 = [item for url in urls1 for item in requests.get(url).json()["listings"]]
        cars3 = cars1.copy()
        newest_car_id_1, cars1 = filter_ads1(cars1, CONFIG_PRICE1_2, newest_car_id_1)

        check_ads(
            config=config1, 
            filtered_ads = cars1,
            chat_id=CHAT_ID1,
            function_for_message=create_cars_bot_message, 
        )

        cars2 = [item for url in urls2 for item in requests.get(url).json()["listings"]]
        cars4 = cars2.copy()
        newest_car_id_2, cars2 = filter_ads1(cars2, CONFIG_PRICE1_2, newest_car_id_2)

        check_ads(
            config=config2,
            filtered_ads=cars2, 
            chat_id=CHAT_ID1,
            function_for_message=create_cars_bot_message, 
        )

        newest_car_id_3, cars3 = filter_ads2(cars3, CONFIG_PRICE5, newest_car_id_3)

        check_ads(
            config=config1, 
            filtered_ads=cars3, 
            chat_id=CHAT_ID2,
            function_for_message=create_cars_bot_message, 
        )

        newest_car_id_4, cars4 = filter_ads2(cars4, CONFIG_PRICE5, newest_car_id_4)

        check_ads(
            config=config2,
            filtered_ads=cars4, 
            chat_id=CHAT_ID2,
            function_for_message=create_cars_bot_message, 
        )

        wheels1 = [item for url in urls3 for item in requests.get(url).json()["listings"]]
        newest_wheel_id_1, wheels1 = filter_ads1(wheels1, CONFIG_PRICE3_4, newest_wheel_id_1)

        check_ads(
            config=config3, 
            filtered_ads=wheels1, 
            chat_id=CHAT_ID3,
            function_for_message=create_wheels_bot_message, 
        )

        wheels2 = [item for url in urls4 for item in requests.get(url).json()["listings"]]
        newest_wheel_id_2, wheels2 = filter_ads1(wheels2, CONFIG_PRICE3_4, newest_wheel_id_2)
        
        check_ads(
            config=config4, 
            filtered_ads=wheels2, 
            chat_id=CHAT_ID3,
            function_for_message=create_wheels_bot_message, 
        )

        print(newest_car_id_1, newest_car_id_2, newest_car_id_3, newest_car_id_4, newest_wheel_id_1, newest_wheel_id_2)

        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
