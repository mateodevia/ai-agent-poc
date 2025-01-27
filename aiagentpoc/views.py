from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from aiagentpoc.agents.agents import available_agents
from auth.simple_api_key import validate_simple_api_key, AuthenticationException
import json
import traceback

def get_agent_response(agent, client_prompt):
    agent_response = agent.run(client_prompt)
    text_response = agent_response.messages[-1].content
    return text_response


@csrf_exempt
def post_prompt(request):
    load_dotenv()

    try:
        validate_simple_api_key(request)
        
        body = json.loads(request.body.decode('utf-8'))
        agent_name = body["agent"]
        client_prompt = body["prompt"]
        client_id = body["clientId"]
        agent_options = body["agentOptions"]

        agent_constructor = available_agents.get(agent_name)
        if agent_constructor == None:
            return HttpResponseNotFound("Agent not found")
        
        agent = agent_constructor(client_id, client_prompt, agent_options)
        agent_response = get_agent_response(agent, client_prompt)

        return JsonResponse({
            "agentResponse": agent_response,
        })
    
    except AuthenticationException as e:
        print("Auth error:", e)
        return HttpResponseForbidden("Forbidden")
    
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            "agentResponse": "Lo siento, en este momento no me encuentro disponible. Intentalo de nuevo más tarde",
        })