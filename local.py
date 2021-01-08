import os, json, bot, auth, logging, traceback

from bottle import (  
    run, post, route, get, response, request as bottle_request
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s:%(message)s')

@post('/') # Local server for testing (not actually deployed)
def main():
    try:
        logging.info(json.dumps(bottle_request.json, indent=4, sort_keys=True))
        return bot.handler({"body": bottle_request.json}, "local server")
    except Exception as err:
        logging.error(traceback.format_exc())
        return {
            "error": str(err)
        }
	
@get('/auth')
def authentication():
    try:
        event = {
            "queryStringParameters": {
                "code": bottle_request.query.get("code"),
                "state": bottle_request.query.get("state"),
            },
            "headers": {
                "Host": bottle_request.urlparts.netloc
            },
            "requestContext": {
                "path": bottle_request.urlparts.path
            } 
        }
        logging.info(json.dumps(event, indent=4, sort_keys=True))
        return auth.handler(event, "local server")
    except Exception as err:
        logging.error(traceback.format_exc())
        return {
            "error": str(err)
        }

if __name__ == '__main__':  
    run(host='localhost', port=5000, debug=True)
