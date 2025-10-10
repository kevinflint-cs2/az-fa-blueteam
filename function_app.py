import azure.functions as func
from functions.helloworld import helloworld as helloworld_logic
from functions.goodbye import goodbye as goodbye_logic
from functions.abuseipdb import check_ip, report_ip

app = func.FunctionApp()
@app.route(route="abuseipdb/check", auth_level=func.AuthLevel.FUNCTION)
def abuseipdb_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for checking an IP with AbuseIPDB.
    Expects 'ip' as a query or JSON parameter.
    """
    ip = req.params.get("ip")
    if not ip:
        try:
            req_body = req.get_json()
        except ValueError:
            ip = None
        else:
            ip = req_body.get("ip")
    if not ip:
        return func.HttpResponse("Missing required parameter: ip", status_code=400)
    try:
        result = check_ip(ip)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


@app.route(route="abuseipdb/report", auth_level=func.AuthLevel.FUNCTION)
def abuseipdb_report(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for reporting an IP to AbuseIPDB.
    Expects 'ip', 'categories', and 'comment' as parameters.
    """
    ip = req.params.get("ip")
    categories = req.params.get("categories")
    comment = req.params.get("comment")
    if not ip or not categories or not comment:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        ip = ip or req_body.get("ip")
        categories = categories or req_body.get("categories")
        comment = comment or req_body.get("comment")
    if not ip or not categories or not comment:
        return func.HttpResponse("Missing required parameters: ip, categories, comment", status_code=400)
    try:
        result = report_ip(ip, categories, comment)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


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
