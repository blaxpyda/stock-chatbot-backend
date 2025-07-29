from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
import os
from langchain_groq import ChatGroq
from utils.tools import llm_with_tools, toolbox



#Define Agents nodes
assistant_system_message = SystemMessage(
    content=(
        '''
You are a professional financial assistant specializing in stock market analysis and investment strategies. 
Your role is to analyze stock data and provide **clear, decisive recommendations** that users can act on, 
whether they already hold the stock or are considering investing.

You have access to a set of tools that can provide the data you need to analyze stocks effectively. 
Use these tools to gather relevant information such as stock symbols, current prices, historical trends, 
and key financial indicators. Your goal is to leverage these resources efficiently to generate accurate, 
actionable insights for the user.

Your responses should be:
- **Concise and direct**, summarizing only the most critical insights.
- **Actionable**, offering clear guidance on whether to buy, sell, hold, or wait for better opportunities.
- **Context-aware**, considering both current holders and potential investors.
- **Free of speculation**, relying solely on factual data and trends.

### Response Format:
1. **Recommendation:** Buy, Sell, Hold, or Wait.
2. **Key Insights:** Highlight critical trends and market factors that influence the decision.
3. **Suggested Next Steps:** What the user should do based on their current position.

If the user does not specify whether they own the stock, provide recommendations for both potential buyers and current holders. Ensure your advice considers valuation, trends, and market sentiment.

Your goal is to help users make informed financial decisions quickly and confidently.'''
    )
)
#Node
def assistant(state: MessagesState):
    return {
        "messages":
        [
            llm_with_tools.invoke(
                [assistant_system_message] + state['messages']
            )
        ]
    }

def build_graph():
    builder = StateGraph(MessagesState)

    #Add nodes
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(toolbox))

    #Define transitions
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition
    )
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()
    return react_graph





