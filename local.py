import os, json, handler

from bottle import (  
    run, post, response, request as bottle_request
)

@post('/') # Local server for testing (not actually deployed)
def main():
    try:
        print(json.dumps(bottle_request.json, indent=4, sort_keys=True))
        return handler.trigger({"body": bottle_request.json}, "local server")
    except Exception as err:
        print(err)
        return {
            "error": str(err)
        }
	
if __name__ == '__main__':  
    run(host='localhost', port=5000, debug=True)
