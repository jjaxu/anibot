import os, json, handler, logging, traceback

from bottle import (  
    run, post, response, request as bottle_request
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s:%(message)s')

@post('/') # Local server for testing (not actually deployed)
def main():
    try:
        logging.info(json.dumps(bottle_request.json, indent=4, sort_keys=True))
        return handler.trigger({"body": bottle_request.json}, "local server")
    except Exception as err:
        logging.error(traceback.format_exc())
        return {
            "error": str(err)
        }
	
if __name__ == '__main__':  
    run(host='localhost', port=5000, debug=True)
