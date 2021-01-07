import requests, logging, os, json

AUTH_URL = "https://anilist.co/api/v2/oauth/token"
CLIENT_ID = os.environ['ANIBOT_CLIENT_ID']
CLIENT_SECRET = os.environ['ANIBOT_CLIENT_SECRET']

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s:%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Received auth event: {event}")
    
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": event["queryStringParameters"]["code"],
        "redirect_uri": f"https://{event['headers']['Host']}{event['requestContext']['path']}"
    }
    
    res = requests.post(AUTH_URL, json=data)

    if not res.ok:
        logger.error(f"Failed to get auth token: {res.text}")
        res.raise_for_status()

    res_json = res.json()

    access_token = res_json["access_token"]
    refresh_token = res_json["refresh_token"]
    expiration = res_json["expires_in"]

    logger.info("Successful authorized Anibot!")

    # TODO: Store token in DB

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully authorized Anibot! You may now close this window and return to Telegram."})
    }
