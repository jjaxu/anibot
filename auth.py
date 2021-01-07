import requests, logging, os, json

AUTH_URL = "https://anilist.co/api/v2/oauth/token"
CLIENT_ID = os.environ['ANIBOT_CLIENT_ID']
CLIENT_SECRET = os.environ['ANIBOT_CLIENT_SECRET']

def handler(event, context):
    logging.info(f"Received auth event: {event}")
    print(event)
    
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": event["queryStringParameters"]["code"],
        "redirect_uri": f"https://{event['headers']['Host']}{event['requestContext']['path']}"
    }
    
    print(data)
    
    res = requests.post(AUTH_URL, json=data)

    if not res.ok:
        logging.error(f"Failed to get auth token: {res.text}")
        res.raise_for_status()

    res_json = res.json()

    access_token = res_json["access_token"]
    refresh_token = res_json["refresh_token"]
    expiration = res_json["expires_in"]

    print("Successful authorized Anibot!")
    print(res_json)

    # TODO: Store token in DB

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully authorized Anibot! You may now close this window and return to Telegram."})
    }
