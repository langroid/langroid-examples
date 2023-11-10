To build cloud-langroid image, run the following.

```
docker build -t cloud-langroid .
```

Then deploy the pod using,

```
docker run --env-file .env  -p 8080:8080 cloud-langroid
```

Example usage,

# Create an agent.
curl -X POST http://localhost:8080/langroid/agent -H "Content-Type: application/json" -d '{"agent_name": "agent-1"}'

# Get LLM response from the created agent agent.
curl -X POST http://127.0.0.1:8080/langroid/agent/completions -H "Content-Type: application/json" -d '{"agent_name": "agent-1", "prompt": "what is the capital of India?"}'