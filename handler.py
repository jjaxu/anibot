import json

# Very basic example of a lambda handler
def hello(event, context):
    body = {
        "message": "Hello Anibot!"
    }

    # Remove
    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
