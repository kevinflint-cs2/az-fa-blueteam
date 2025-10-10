import azure.functions as func
from functions.helloworld import helloworld as helloworld_logic
from functions.goodbye import goodbye as goodbye_logic

app = func.FunctionApp()


@app.route(route="helloworld", auth_level=func.AuthLevel.FUNCTION)
def helloworld(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            name = None
        else:
            name = req_body.get("name")

    if name:
        return func.HttpResponse(helloworld_logic(name))
    else:
        return func.HttpResponse("Please provide a name parameter.", status_code=400)


@app.route(route="goodbye", auth_level=func.AuthLevel.FUNCTION)
def goodbye(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            name = None
        else:
            name = req_body.get("name")

    if name:
        return func.HttpResponse(goodbye_logic(name))
    else:
        return func.HttpResponse("Please provide a name parameter.", status_code=400)
