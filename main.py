from fastapi import FastAPI, HTTPException, Query
import requests
import os
import uvicorn
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="GeckoTerminal API V2",
    description="API wrapper for GeckoTerminal Public API V2",
    version="1.0.0"
)

BASE_URL = "https://api.geckoterminal.com/api/v2"
API_VERSION = "20230302"

# Helper function to send requests to GeckoTerminal
def fetch_from_geckoterminal(endpoint: str, params: Optional[Dict[str, Any]] = None):
    url = f"{BASE_URL}{endpoint}"
    
    headers = {
        "Accept": f"application/json;version={API_VERSION}",
        "User-Agent": "GeckoTerminal-API-Wrapper/1.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

@app.get("/")
def home():
    return {
        "message": "✅ GeckoTerminal API V2 Wrapper is running!",
        "version": "1.0.0",
        "api_version": API_VERSION
    }

@app.get("/networks")
def get_supported_networks():
    """
    Get list of supported networks
    """
    return fetch_from_geckoterminal("/networks")

@app.get("/networks/{network}/dexes")
def get_network_dexes(network: str):
    """
    Get list of supported dexes on a specific network
    """
    return fetch_from_geckoterminal(f"/networks/{network}/dexes")

@app.get("/networks/trending_pools")
def get_trending_pools(
    limit: Optional[int] = Query(10, description="Number of trending pools to return")
):
    """
    Get trending pools across all networks
    """
    params = {"limit": limit}
    return fetch_from_geckoterminal("/networks/trending_pools", params)

@app.get("/networks/{network}/trending_pools")
def get_network_trending_pools(
    network: str,
    limit: Optional[int] = Query(10, description="Number of trending pools to return")
):
    """
    Get trending pools on a specific network
    """
    params = {"limit": limit}
    return fetch_from_geckoterminal(f"/networks/{network}/trending_pools", params)

@app.get("/networks/{network}/tokens/{token_address}")
def get_token_details(network: str, token_address: str):
    """
    Get specific token details on a network
    """
    return fetch_from_geckoterminal(f"/networks/{network}/tokens/{token_address}")

@app.get("/simple/networks/{network}/token_price/{addresses}")
def get_token_prices(
    network: str, 
    addresses: str
):
    """
    Get current USD prices of multiple tokens on a network
    """
    return fetch_from_geckoterminal(f"/simple/networks/{network}/token_price/{addresses}")

@app.get("/search/pools")
def search_pools(
    query: str = Query(..., description="Search query for pools"),
    limit: Optional[int] = Query(10, description="Number of results to return")
):
    """
    Search for pools
    """
    params = {
        "query": query,
        "limit": limit
    }
    return fetch_from_geckoterminal("/search/pools", params)

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8089))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting GeckoTerminal API Wrapper on {host}:{port}")
    
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=True
    )
