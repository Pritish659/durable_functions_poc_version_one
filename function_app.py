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
def customer_list_orchestrator(context):
    """List all customers and call another orchestrator
    to process further for each customer parallelly"""
    path = 'config/params.json'
    list_of_customers = yield context.call_activity("list_customers",path)
    tasks_customers = []
    for customer in list_of_customers:
        tasks_customers.append(context.call_sub_orchestrator(name="customer_orchestrator",input_=customer))
    customers = yield context.task_all(tasks_customers)
    return customers


@myApp.activity_trigger(input_name="path")
def list_customers(path: str):
    """Get the list of customers with their config"""
    with open(path) as f:
        customer_list = json.load(f) 
    return customer_list

# Sub Orchestrator
@myApp.orchestration_trigger(context_name="context")
def customer_orchestrator(context):
    """Get all open tickets for a customer and
    call another orchestrator for further processing"""
    input_ = context.get_input()
    list_of_open_tickets = yield context.call_activity("customer_details",input_)
    task_tickets = []
    for ticket in list_of_open_tickets:
         task_tickets.append(context.call_sub_orchestrator(name="ticket_orchestrator",input_=ticket))
    ticket_ids = yield context.task_all(task_tickets)
    return ticket_ids


@myApp.activity_trigger(input_name="customer")
def customer_details(customer: str):
    """Get all open tickets"""
    return customer["tickets"]

# Sub-Sub Orchestrator
@myApp.orchestration_trigger(context_name="context")
def ticket_orchestrator(context):
    """Process one ticket detail at a time"""
    input_ = context.get_input()
    ticket_id = yield context.call_activity("ticket_details",input_)
    return ticket_id


@myApp.activity_trigger(input_name="ticket")
def ticket_details(ticket: str):
    """Get ticket_id for an id"""
    return ticket["ticket_id"]