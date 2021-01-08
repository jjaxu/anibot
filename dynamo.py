import boto3, os

USERS_TABLE = os.environ["USERS_TABLE_NAME"]
STAGE = os.environ.get("STAGE", "local")

def put_item(telegram_id: str, access_token: str) -> None:
    if STAGE == "local": # Local
        session = boto3.Session(profile_name='botprofile')
        dbClient = session.client('dynamodb')
    else: # Aws
        dbClient = boto3.client('dynamodb')    
    
    dbClient.put_item(
        TableName=USERS_TABLE,
        Item={
            'telegramId': {
                'S': str(telegram_id)
            },
            'accessToken': {
                'S': str(access_token)
            }
        }
    )
