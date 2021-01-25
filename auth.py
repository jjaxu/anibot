import requests, logging, os, json, dynamo, utils, anilist

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
        "code": event["queryStringParameters"].get("code", ""),
        "redirect_uri": f"https://{event['headers']['Host']}{event['requestContext']['path']}"
    }
    
    res = requests.post(AUTH_URL, json=data)

    if not res.ok:
        logger.error(f"Failed to get auth token: {res.text}")
        return {
            "statusCode": res.status_code,
            "body": json.dumps({"error": "Failed authorize via AniList, please try again later."})
        }

    res_json = res.json()

    access_token = res_json.get("access_token")
    if not access_token:
        logger.warning(f"User denied Anilist access: {res_json.get('error', '')}")
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Authorization failed, you can always try again."})
        }
    
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

    sender_id = sender_data["sender_id"]

    logger.info(f"Successfully authorized Anibot for user: {sender_data}")

    # Verify token
    userInfo = anilist.getUserInfo(access_token)
    if not userInfo:
        logger.error("Failed verify access token")
        return {
            "statusCode": 503,
            "body": json.dumps({"message": f"Failed to authorize Anibot, the access token may be expired."})
        }

    aniList_id, aniList_userName = userInfo
        
    # Store in DB
    # TODO: check existing token first
    try:
        dynamo.put_item(sender_id, access_token, aniList_id, aniList_userName)
    except Exception as err:
        logger.error(f"Failed save data to dynamoDB. Error: {err}")
        return {
            "statusCode": 503,
            "body": json.dumps({"message": f"Failed to authorize Anibot for user '{sender_id}', please try again later."})
        }

    
    logger.info(f"Successfully authorized Anibot for user: {sender_data}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Successfully authorized Anibot for '{userInfo[1]}'! You may now close this window and return to Telegram."})
    }
