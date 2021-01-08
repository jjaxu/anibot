import requests, logging, os, json, dynamo, utils

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
        return {
            "statusCode": res.status_code,
            "body": json.dumps({"error": "Failed authorize user via AniList, please try again later."})
        }

    res_json = res.json()

    access_token = res_json["access_token"]
    
    # Parse state to identify user
    sender_data = None
    try:
        sender_data = json.loads(utils.decode_to_base64_string(event["queryStringParameters"]["state"]))
    except Exception as err:
        logger.error(f"Failed to identify user, state data is invalid. Error: {err}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Failed to identify user, are you using a stale link?"})
        }

    sender_name = sender_data["sender_name"]
    sender_id = sender_data["sender_id"]

    logger.info(f"Successfully authorized Anibot for user: {sender_data}")

    # Store in DB
    try:
        dynamo.put_item(sender_id, access_token)
    except Exception as err:
        logger.error(f"Failed save data to dynamoDB. Error: {err}")
        return {
            "statusCode": 503,
            "body": json.dumps({"message": f"Failed to authorize Anibot as '{sender_name}', please try again later."})
        }

    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Successfully authorized Anibot as '{sender_name}'! You may now close this window and return to Telegram."})
    }
