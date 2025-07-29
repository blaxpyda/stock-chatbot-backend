import os
import requests
from pprint import pprint, pformat
import yfinance as yf
import json
from langchain_core.tools import Tool, tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

@tool
def lookup_stock_symbol(company_name: str) -> str:
    '''
    Convert a company name to its stock symbol using the Alpha Vantage API.
    
    Args:
        company_name (str): The name of the company to look up.
    Returns:
        str: The stock symbol of the company.
    '''
    api_url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": os.getenv('ALPHA_VANTAGE_API_KEY')
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    if 'bestMatches' in data and data['bestMatches']:
        # Return the first match's symbol
        return data['bestMatches'][0]['1. symbol']
    else:
        raise ValueError(f"No stock symbol found for company: {company_name}")
    
def fetch_stock_data(symbol: str, period: str = '1mo') -> dict:
    '''
    Fetch comprehensive stock data for a given symbol and returns it as a dictionary.
    
    Parameters:
        symbol (str): The stock symbol to fetch data for.
        period (str): The time period for which to fetch data. Default is '1mo'.
        
    Returns:
        dict: A dictionary containing the stock data.
    '''

    try:
        stock = yf.Ticker(symbol)

        # Fetch historical market data
        stock_info = stock.info
        stock_history = stock.history(period=period).to_dict()

        #Combine info and history into a single dictionary
        combined_data = {
            'stock_symbol': symbol,
            'info': stock_info,
            'history': stock_history
        }
        return pformat(combined_data)
    except Exception as e:
        return {"error": f"Error fetching data for {symbol}: {str(e)}"}
    
#Bind the tools
#Create tool bindings with additional attributes
# lookup_stock = Tool.from_function(
#     func=lookup_stock_symbol,
#     name="lookup_stock_symbol",
#     description="Lookup the stock symbol for a given company name.",
#     return_direct = False # Return result to be processed by the LLM
# )
fetch_stock = Tool.from_function(
    func=fetch_stock_data,
    name="fetch_stock_data",
    description="Fetch stock data for a given symbol.",
    return_direct = False
)

toolbox = [lookup_stock_symbol, fetch_stock]

simple_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv('GROQ_API_KEY'),
)
llm_with_tools = simple_llm.bind_tools(toolbox)
# load =fetch_stock_data('TSLA')
# print(load)

# if __name__ == "__main__":
#     stock = llm_with_tools.invoke(
#          [
#                 HumanMessage(content="What is the stock symbol for Tesla?"),
#             ]
        
#     )
#     pass
