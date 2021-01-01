import os, json, requests, logging

from anilist import getAnime

TOKEN = os.environ['ANIBOT_TOKEN']
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s:%(message)s')

# The entry point to the function
# event should have the format { "body": json_obj }
def trigger(event, context):
    data = event["body"]

    logging.debug(f"Received event with content: {data}; context: {context}")

    body = {
        "message": "Hello Anibot 3!",
        "request": data
    }
    
    # Normal Query
    # telegram_response = {
    #     "chat_id": data["message"]["chat"]["id"],
    #     "text": f"Hello from Anibot 3! ({str(context)})"
    # }

    # url = TELEGRAM_BASE_URL + "/sendMessage"
    # res = requests.post(url, json=telegram_response)
    # if not res.ok:
    #     logging.error(f"Telegram failed to send the message: error code {res.status_code}, message: {res.text}")

    handle_inline_query(data)

    # Remove
    return {
        "statusCode": 200,
        "body": body
    }

def handle_inline_query(data):
    query_id = data["inline_query"]["id"]
    query = data["inline_query"]["query"]

    animeList = getAnime(query)


    results = []

    index = 1
    for anime in animeList:
        results.append({
            "type": "article",
            "id": str(index),
            "title": f'{anime["title"]["english"]} ({anime["title"]["romaji"]})',
            "input_message_content": {
                "message_text": anime["description"]
            },
            # "url": "https://anilist.co/anime/116267/Tonikaku-Kawaii/",
            "description": anime["description"],
            "thumb_url": anime["coverImage"]["medium"]
        })
        index += 1





    # Inline Article
    pic = {
        "type": "article",
        "id": "1",
        "title": "Tonikaku-Kawaii",
        "input_message_content": {
            "message_text": "ok"
        },
        "url": "https://anilist.co/anime/116267/Tonikaku-Kawaii/",
        "description": "The story follows a protagonist whose name is written with the characters for \"Hoshizora\" (\"Starry Sky\" in Japanese), but whose name is pronounced as \"Nasa\". On the day of his high school entrance exams, Nasa encounters a beautiful girl named Tsukasa. For Nasa, it feels like destiny is finally calling out to him that he will have a girlfriend, but things take a turn for the worse when Nasa is hit by a car and unable to attend his entrance exams.",
        "thumb_url": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/b116267-JArFvMYRdnbd.jpg"
    }

        # Inline Article
    pic2 = {
        "type": "article",
        "id": "2",
        "title": "Shingeki no Kyojin",
        "input_message_content": {
            "message_text": "ok"
        },
        "url": "https://anilist.co/anime/16498/Shingeki-no-Kyojin/",
        "description": "Several hundred years ago, humans were nearly exterminated by titans. Titans are typically several stories tall, seem to have no",
        "thumb_url": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-m5ZMNtFioc7j.png"
    }

    print(f"num found: {len(results)}")

    data = {
        'inline_query_id': query_id,
        'results': results
    }
    url = TELEGRAM_BASE_URL + "/answerInlineQuery"
    res = requests.post(url, json=data)
