import azure.functions as func
import azure.durable_functions as df
import json
myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# An HTTP-Triggered Function with a Durable Functions Client binding
@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response

# Orchestrator
@myApp.orchestration_trigger(context_name="context")
def hello_orchestrator(context):
    # test = print(context.get_input('config/params.json'))
    path = 'config/params.json'
    list_of_customers = yield context.call_activity("list_customers",path)
    result1 = yield context.call_activity("hello_city", "Bengaluru")
    result2 = yield context.call_activity("hello_state", "Karnataka")
    result3 = yield context.call_activity("hello_country", "India")
    return [result1, result2, result3, list_of_customers]

# list the customers
@myApp.activity_trigger(input_name="path")
def list_customers(path: str):
    with open(path) as f:
        customer_list = json.load(f) 
    return f"{customer_list}"

# Activity function 1
@myApp.activity_trigger(input_name="city")
def hello_city(city: str):
    return f"Hello from PhData {city}"

# Activity function 2
@myApp.activity_trigger(input_name="state")
def hello_state(state: str):
    return f"Hello from PhData {state}"

# Activity function 3
@myApp.activity_trigger(input_name="country")
def hello_country(country: str):
    return f"Hello from PhData {country}"