from fastapi import FastAPI
# Relative imports because this file is part of the 'zuno' package
from .models import AgentRequest, AgentResponse
from .agents import OrchestratorAgent

app = FastAPI(title="Zuno MCP Server")
orchestrator = OrchestratorAgent()

@app.post("/invoke_agent", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    The single entry point for the Zuno agent system.
    It accepts a structured request and returns a structured response.
    """
    response = orchestrator.run(request)
    return response

@app.get("/")
def root():
    return {"message": "Zuno MCP Server is running."}


# This block allows us to run the server directly with 'python -m zuno.server'
if __name__ == "__main__":
    import uvicorn
    # The string "zuno.server:app" tells uvicorn where to find the FastAPI 'app' object.
    uvicorn.run("zuno.server:app", host="127.0.0.1", port=8000, reload=True)