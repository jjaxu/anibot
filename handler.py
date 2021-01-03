import os, json, requests, logging

from anilist import getAnime
from htmlParser import strip_tags

TOKEN = os.environ['ANIBOT_TOKEN']
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
MAX_ITEMS = 20

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

    # inline query can only return up to 20 items
    for idx in range(min(MAX_ITEMS, len(animeList))):
        anime = animeList[idx]

        # Format data
        title = anime["title"]["romaji"]
        if anime["title"]["english"]:
            title = f'{title} ({anime["title"]["english"]})'

        description = anime["description"] or "(no description)"
        description_no_markup = strip_tags(description)
        description_html = description.replace("<br>", "")

        siteUrl = anime["siteUrl"]

        msg_body = (
            f"<b>Title:</b> <i>{title}</i>\n"
            f"<b>Average score:</b> {anime['averageScore'] or '-' }\n"
            f"<b>Episodes:</b> {anime['episodes']}\n\n"

            # f"{description_html}\n"

            f"<a href=\"{siteUrl}\">View on AniList</a>"
        )

        # Add data to result
        results.append({
            "type": "article",
            "id": str(idx),
            "title": title,
            "input_message_content": {
                "message_text": msg_body,
                "parse_mode": "html"
            },
            "url": siteUrl,
            "description": f'({anime["averageScore"] or "-"}) ' + description_no_markup,
            "thumb_url": anime["coverImage"]["medium"],
        })

    data = {
        'inline_query_id': query_id,
        'results': results
    }
    url = TELEGRAM_BASE_URL + "/answerInlineQuery"
    res = requests.post(url, json=data)

    if not res.ok:
        logging.error(f"Failed to answer inline query: {res.text}")
