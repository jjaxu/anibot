import boto3, os, json

USERS_TABLE = os.environ["USERS_TABLE_NAME"]
STAGE = os.environ.get("STAGE", "local")

def get_users_table():
    if STAGE == "local": # Local
        session = boto3.Session(profile_name='botprofile')
        return session.resource('dynamodb').Table(USERS_TABLE)
    return boto3.resource('dynamodb').Table(USERS_TABLE)  
    
def put_item(telegram_id: str, access_token: str, aniList_id: int, aniList_userName: str) -> None:
    table = get_users_table()
    table.put_item(Item={
        'telegramId': str(telegram_id),
        'accessToken': str(access_token),
        'aniListId': str(aniList_id),
        'aniListUserName': str(aniList_userName)
    })

def get_item(telegram_id: str):
    table = get_users_table()
    res = table.get_item(Key={ 'telegramId': str(telegram_id) })
    return res.get('Item')

def delete_item(telegram_id: str):
    table = get_users_table()
    res = table.delete_item(Key={ 'telegramId': str(telegram_id) })
