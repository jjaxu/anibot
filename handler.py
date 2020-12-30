import os, json, requests

TOKEN = os.environ['ANIBOT_TOKEN']
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# The entry point to the function
# event should have the format { "body": json_obj }
def trigger(event, context):
    data = event["body"]
    body = {
        "message": "Hello Anibot 3!",
        "request": data
    }

    telegram_response = {
        "chat_id": data["message"]["chat"]["id"],
        "text": f"Hello from Anibot 3! ({str(context)})"
    }

    url = TELEGRAM_BASE_URL + "/sendMessage"
    res = requests.post(url, json=telegram_response)
    if not res.ok:
        print(res.status_code)
        print(res.text)

    # Remove
    return {
        "statusCode": 200,
        "body": body
    }
