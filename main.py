from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.graph import build_graph
from langchain_core.messages import HumanMessage
from pydantic import BaseModel



react_graph = build_graph()


app = FastAPI()

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    input_data: str

@app.post('/agent/')
async def run_agent(request: AgentRequest):
    """
    Endpoint to run the agent with the provided input data.
    """
    # Prepare the initial state for the graph
    initial_state = {
        "messages": [
            HumanMessage(content=request.input_data)
        ]
    }
    
    # Invoke the graph with the initial state
    result = react_graph.invoke(initial_state)
    
    # Return the result
    response_content = result['messages'][-1].content if result['messages'] else "No response generated."
    return {"response": response_content}