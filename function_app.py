import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.route(route="helloworld", auth_level=func.AuthLevel.FUNCTION)
def helloworld(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            name = None
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}")
    else:
        return func.HttpResponse("Please provide a name parameter.", status_code=400)


# Goodbye function
@app.route(route="goodbye", auth_level=func.AuthLevel.FUNCTION)
def goodbye(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            name = None
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Goodbye, {name}")
    else:
        return func.HttpResponse("Please provide a name parameter.", status_code=400)