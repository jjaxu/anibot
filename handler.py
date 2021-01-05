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
    
    # Inline query
    if data.get("inline_query"):
        handle_inline_query(data)
    else: # Normal query
        handle_normal_query(data)

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
        episodes_or_volumes_label = "Episodes" if anime["type"] == "ANIME" else "Volumes"

        msg_body = (
            f"<i>{title}</i>\n\n"
            f"<b>Type:</b> {anime.get('type', '-').title()}\n"
            f"<b>Status:</b> {anime.get('status', '-').title().replace('_', ' ') }\n"
            f"<b>Average score:</b> {anime.get('averageScore', '-') }\n"
            f"<b>{episodes_or_volumes_label}:</b> {anime.get(episodes_or_volumes_label.lower(), '-')}\n"
            f"<a href=\"{siteUrl}\">&#x200b;</a>" # To show preview, use a zero-width space
        )

        inline_description = " ".join(
            (
                f"[{anime['type']}]" if anime['type'] else "",
                f"({anime['averageScore']})" if anime['averageScore'] else "",
                description_no_markup
            )
        )
        
        # Add data to result
        results.append({ # InlineQueryResultArticle
            "type": "article",
            "id": str(idx),
            "title": title,
            "input_message_content": { # InputMessageContent
                "message_text": msg_body,
                "parse_mode": "html",
            },
            "reply_markup": { # InlineKeyboardMarkup
                "inline_keyboard": 
                [
                    [
                        {
                            "text": "View on Anilist",
                            "url": siteUrl
                        }
                    ]
                ],
            },
            "url": siteUrl,
            "description": inline_description,
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
        res.raise_for_status()


def handle_normal_query(data):
    pass
    # Normal Query
    # telegram_response = {
    #     "chat_id": data["message"]["chat"]["id"],
    #     "text": f"Hello from Anibot 3! ({str(context)})"
    # }

    # url = TELEGRAM_BASE_URL + "/sendMessage"
    # res = requests.post(url, json=telegram_response)
    # if not res.ok:
    #     logging.error(f"Telegram failed to send the message: error code {res.status_code}, message: {res.text}")
