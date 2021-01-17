import os, json, requests, logging, random, utils, dynamo

from anilist import getAnime, getAnimeList, increaseProgress
from htmlParser import strip_tags
from botquery import BotQuery

TOKEN = os.environ['ANIBOT_TOKEN']
CLIENT_ID = os.environ['ANIBOT_CLIENT_ID']
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
MAX_ITEMS = 20

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s:%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# The entry point to the function
def handler(event, context):
    data = event["body"]

    logger.info(f"Received event with content: {data}; context: {context}")

    body = {
        "message": "Hello Anibot 3!",
        "request": data
    }

    try:
        query = BotQuery.parse_event(data)
    except Exception as err:
        logger.error(f"Unsupported query: {err}")
        return
    
    # Inline query
    if query.is_inline_query:
        handle_inline_query(query)
    elif query.has_callback_query:
        handle_callback_query(query)
    elif query.message: # Normal query
        handle_normal_query(data)
    else:
        logger.warning("Received unknown request, skipping...")

    # Remove
    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def handle_inline_query(query: BotQuery):
    query_id = query.inline_query_id
    query = query.inline_query_text

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
        episodes_or_volumes_label = "episodes" if anime["type"] == "ANIME" else "volumes"

        msg_body = (
            f"&#x1F1EF;&#x1F1F5; <i>{title_japanese}</i>\n"
            f"{title_english_formatted}\n"
            f"<b>Type:</b> {(anime['type'] or '-').title()} ({(anime['format'] or '-').replace('_', ' ')})\n"
            f"<b>Status:</b> {(anime['status'] or '-').title().replace('_', ' ') }\n"
            f"<b>Average score:</b> {anime['averageScore'] or '-' }%\n"
            f"<b>{episodes_or_volumes_label.title()}:</b> { (anime[episodes_or_volumes_label] or '-') }\n"
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
                        { # InlineKeyboardButton
                            "text": "View on Anilist",
                            "url": siteUrl
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
        logger.error(f"Failed to answer inline query: {res.text}")
        res.raise_for_status()


def handle_normal_query(data):
    msg = data["message"]

    if msg.get("via_bot") and msg["via_bot"]["username"] == "theanibot":
        handle_bot_response(msg)
        return
    
    try:
        query = BotQuery.parse_event(data)
    except Exception as err:
        logger.error(f"Unsupported query: {err}")
        return
    
    msg = query.message.replace("@theanibot", "")

    if msg.startswith("/debug"):
        return
        # send_message(query.chat_id, vars(query))
    elif msg.startswith("/login"):
        handle_login_command(query)
    elif msg.startswith("/logout"):
        handle_logout_command(query)
    elif msg.startswith("/watch"):
        handle_watch_command(query)

def handle_watch_command(query: BotQuery):
    if query.is_group:
        send_security_message(query.chat_id)
        return

    userInfo = None
    try:
        userInfo = dynamo.get_item(query.from_id)
    except Exception as err:
        logging.error(f"Failed to fetch user info from dynamodb. Error: {err}")
        send_message(query.chat_id, f"This feature is currently unavilable, please check back later.")
        return

    if userInfo is None:
        send_message(query.chat_id, "Please log in first! (via the /login command or the button below)", {
            "reply_markup": { # InlineKeyboardMarkup
                "inline_keyboard": 
                [
                    [
                        {
                            "text": "Log in",
                            "url": get_login_url(query.from_id, query.user_first_name)
                        }
                    ]
                ]
            }})
        return

    mediaList = sorted(getAnimeList(userInfo["aniListId"]), key=lambda x: x['media']['title']['romaji'])
    buttons = []
    
    for item in mediaList:
        progress = item['progress']
        anime = item['media']
        episodes = anime['episodes']
        title = anime['title']['romaji'] or anime['title']['english']

        buttons.append(
            [
                {
                    "text": f"{title} ({progress}/{episodes})",
                    "callback_data": "/updateProgress" + json.dumps({
                        "media_id": anime['id']
                    })
                }
            ]
        )
    
    send_message(query.chat_id, (
        "Here's your watchlist, use the buttons to increment the episodes watched." if len(buttons) > 0 else
        "Your watchlist is currently empty, you can add them from AniList."
        ), {
        "reply_markup": { # InlineKeyboardMarkup
            "inline_keyboard": buttons
        },
    })

def handle_login_command(query: BotQuery):
    if query.is_group:
        send_security_message(query.chat_id)
        return
    
    sender_id = query.from_id
    sender_first_name = query.user_first_name

    userInfo = None
    try:
        userInfo = dynamo.get_item(sender_id)
    except Exception as err:
        logging.error(f"Failed to fetch user info from dynamodb. Error: {err}")
        send_message(query.chat_id, f"This feature is currently unavilable, please check back later.")
        return

    is_logged_in = userInfo is not None

    if not is_logged_in:
        send_message(query.chat_id, "You're not currently logged in.", {
            "reply_markup": { # InlineKeyboardMarkup
                "inline_keyboard": 
                [
                    [
                        {
                            "text": "Log in via Anilist",
                            "url": get_login_url(sender_id, sender_first_name)
                        }
                    ]
                ]
            },
        })
    else:
        send_message(query.chat_id, f"You're currently logged in as '{userInfo['aniListUserName']}'. You can use /logout to log out.", {
            "reply_markup": { # InlineKeyboardMarkup
                "inline_keyboard": 
                [
                    [
                        {
                            "text": "Log out",
                            "callback_data": "/logout"
                        }
                    ]
                ]
            },
        })


def handle_logout_command(query: BotQuery):
    if query.is_group:
        send_security_message(query.chat_id)
        return
    logout_user(query.from_id, query.chat_id)

def logout_user(telegram_id: str, chat_id: str):
    try:
        dynamo.delete_item(telegram_id)
    except Exception as err:
        logging.error(f"Failed to delete user info from dynamodb. Error: {err}")
        send_message(chat_id, f"This feature is currently unavilable, please check back later.")
        return
    send_message(chat_id, f"Successful logged out! You can use /login to log in again.")

def handle_bot_response(msg):
    if not msg["text"].startswith(u'\u200b'):
        return

    userName = msg["from"]["first_name"]

    responses = (
        "Mmm… you have interesting taste",
        f"Ooo {userName}, that’s kinda kinky",
        "Ah, I see that you’re a man of culture as well",
        f"{userName}, I didn’t know you were into that",
        "Do your parents know about this?",
        f"Who told you about this one {userName}?",
    )

    send_message(msg["chat"]["id"], random.choice(responses))

def send_message(chat_id: str, text: str, other:dict=None, silent=True):
    request_body = {
        "chat_id": chat_id,
        "text": text,
        "disable_notification": silent
    }

    if other:
        request_body.update(other)

    url = TELEGRAM_BASE_URL + "/sendMessage"
    res = requests.post(url, json=request_body)
    if not res.ok:
        logger.error(f"Telegram failed to send the message: error code {res.status_code}, message: {res.text}")
    
def handle_callback_query(query: BotQuery):
    cb_query = query.callback_query
    if cb_query.callback_data == "/logout":
        logout_user(cb_query.callback_from_id, cb_query.chat_id)
    elif cb_query.callback_data.startswith("/updateProgress"):
        data = json.loads(cb_query.callback_data[len("/updateProgress"):])
        media_id = data['media_id']
        access_token = "abc123" # TODO: fetch from DB
        increaseProgress(access_token, media_id)

        # Gate finished anime
        request_body = {
            "callback_query_id": cb_query.callback_query_id,
            "text": "This feature is still in development, check back later!",
        }

        url = TELEGRAM_BASE_URL + "/answerCallbackQuery"
        res = requests.post(url, json=request_body)
        if not res.ok:
            logger.error(f"Telegram failed to send the message: error code {res.status_code}, message: {res.text}")


def get_security_message() -> str:
    return "Sorry, you cannot use this feature in group chats for security reasons. Please DM me instead!"

def send_security_message(chat_id: str):
    send_message(chat_id, get_security_message(), {
    "reply_markup": { # InlineKeyboardMarkup
        "inline_keyboard": 
            [
                [
                    {
                        "text": "Go to bot's DM",
                        "url": "https://t.me/theanibot"
                    }
                ]
            ]
        },
    })

def get_login_url(sender_id: str, sender_name: str) -> str:
    state_payload = utils.encode_to_base64_string(json.dumps({
        "sender_id": sender_id,
        "sender_name": sender_name
    }))
    return f"https://anilist.co/api/v2/oauth/authorize?client_id={CLIENT_ID}&response_type=code&state={state_payload}"
