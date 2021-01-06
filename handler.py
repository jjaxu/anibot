import os, json, requests, logging, random

from anilist import getAnime
from htmlParser import strip_tags

TOKEN = os.environ['ANIBOT_TOKEN']
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
MAX_ITEMS = 20

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s:%(message)s')

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
    elif data.get("message"): # Normal query
        handle_normal_query(data)
    else:
        logging.warn("Received unknown request")

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
        title_english_formatted = ""

        # Format data
        title_romaji = anime["title"]["romaji"]
        title_english = anime["title"]["english"]
        title_native = anime["title"]["native"]

        title_japanese = title_romaji + (f" ({title_native})" if title_native else "")

        if title_english:
            title_english_formatted = f"&#x1F1FA;&#x1F1F8; <i>{title_english}</i>\n"

        description = anime["description"] or "(no description)"
        description_no_markup = strip_tags(description)
        description_html = description.replace("<br>", "")

        siteUrl = anime["siteUrl"]
        episodes_or_volumes_label = "Episodes" if anime["type"] == "ANIME" else "Volumes"

        msg_body = (
            f"&#x1F1EF;&#x1F1F5; <i>{title_japanese}</i>\n"
            f"{title_english_formatted}\n"
            f"<b>Type:</b> {anime.get('type', '-').title()} ({anime.get('format', '-').replace('_', ' ')})\n"
            f"<b>Status:</b> {anime.get('status', '-').title().replace('_', ' ') }\n"
            f"<b>Average score:</b> {anime.get('averageScore', '-') }\n"
            f"<b>{episodes_or_volumes_label}:</b> {anime.get(episodes_or_volumes_label.lower(), '-')}\n"
            f"<a href=\"{siteUrl}\">&#x200b;</a>" # To show preview, use a zero-width space
        )

        if anime["isAdult"]:
            msg_body += "\n(Details not shown for 18+ series)"

        inline_description = "".join(
            (
                f"[{anime['format'].replace('_', ' ')}] " if anime['format'] else "",
                f"({anime['averageScore']}) " if anime['averageScore'] else "",
                description_no_markup
            )
        )
        
        client_id = 4628

        # Add data to result
        results.append({ # InlineQueryResultArticle
            "type": "article",
            "id": str(idx),
            "title": title_romaji + (f" ({title_english})" if title_english else ""),
            "input_message_content": { # InputMessageContent
                "message_text": (u'\u200b' if anime["isAdult"] else "") + msg_body,
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
                    ],
                    [
                        {
                            "text": "Log in via Anilist",
                            "url": f"https://anilist.co/api/v2/oauth/authorize?client_id={client_id}&response_type=token"
                        }
                    ]
                ]
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
    msg = data["message"]
    if not msg.get("via_bot"):
        return

    if msg["via_bot"]["username"] != "theanibot":
        return

    if not msg["text"].startswith(u'\u200b'):
        return

    # if random.randint(1,10) > 2:
    #     return

    userName = msg["from"]["first_name"]

    responses = (
        "Mmm… you have interesting taste",
        f"Ooo {userName}, that’s kinda kinky",
        "Ah, I see that you’re a man of culture as well",
        f"{userName}, I didn’t know you were into that",
        "Do your parents know about this?",
        f"Who told you about this one {userName}?",
    )

    telegram_response = {
        "chat_id": msg["chat"]["id"],
        "text": random.choice(responses)
    }

    url = TELEGRAM_BASE_URL + "/sendMessage"
    res = requests.post(url, json=telegram_response)
    if not res.ok:
        logging.error(f"Telegram failed to send the message: error code {res.status_code}, message: {res.text}")
