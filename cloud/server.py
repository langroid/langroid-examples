"""
This file defines the cloud langroid server.
"""
from flask import Flask, jsonify, request, render_template

import langroid_agents

app = Flask(__name__)
agent_manager = langroid_agents.AgentManager()

@app.route('/')
def index():
    return render_template('index.html')

# Create endpoint for langroid agent.
@app.route('/langroid/agent', methods=['POST'])
def create_agent():
    # Get the JSON data from the request body
    request_data = request.get_json()
    name = request_data['agent_name']
    agent_name = agent_manager.create_agent(name)

    return jsonify({"message": f"Agent {agent_name} created successfully."}), 200

# Example endpoint to get LLM response.
@app.route('/langroid/agent/completions', methods=['POST'])
def serve_completions():
    # Get the JSON data from the request body
    request_data = request.get_json()

    # Prepare get_agent_response params.
    agent_name = request_data.get('agent_name', 'default')
    llm_prompt = request_data.get('prompt', 'tell me something.')
    
    resp = agent_manager.get_agent_response(agent_name, llm_prompt)
    if resp != None:
        return jsonify({"message": f"{resp}"}), 200
    else:
        return jsonify({"message": "something went wrong"}), 500

if __name__ == '__main__':
    # TODO: Use WSGI server for production.
    app.run(host='0.0.0.0', port=8080)
