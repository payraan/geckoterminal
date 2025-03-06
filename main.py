from fastapi import FastAPI, HTTPException, Query
import requests
import os
import uvicorn
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="GeckoTerminal API",
    description="API for retrieving DeFi data including DEX pairs, tokens, and market information",
    version="1.0.0"
)

BASE_URL = "https://api.geckoterminal.com/api/v2"

@app.get("/")
def home():
    return {"message": "✅ GeckoTerminal API is running!", "version": "1.0.0"}

# Helper function to send requests to GeckoTerminal
async def fetch_from_geckoterminal(endpoint: str, params: Optional[Dict[str, Any]] = None):
    url = f"{BASE_URL}{endpoint}"
    
    print(f"🔍 Sending request to: {url}")
    print(f"🔍 With params: {params}")
    
    try:
        response = requests.get(url, params=params)
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            print(f"❌ Bad Request: {response.text}")
            raise HTTPException(status_code=400, detail=f"❌ Bad Request: {response.text}")
        elif response.status_code == 429:
            print(f"❌ Too Many Requests: {response.text}")
            raise HTTPException(status_code=429, detail="❌ Rate limit exceeded. Please try again later.")
        else:
            print(f"⚠ Unexpected Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"⚠ Unexpected Error: {response.text[:200]}")
    except requests.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Connection Error: {str(e)}")

# 1️⃣ Get trending networks
@app.get("/networks/trending")
async def get_trending_networks(
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)")
):
    """
    Get currently trending blockchain networks
    """
    try:
        result = await fetch_from_geckoterminal("/networks/trending")
        
        # Limit the number of networks returned
        if "data" in result and isinstance(result["data"], list):
            result["data"] = result["data"][:min(limit, 100)]
        
        return result
    except Exception as e:
        print(f"Error in get_trending_networks: {str(e)}")
        raise

# 2️⃣ Get tokens for a specific network
@app.get("/networks/{network_id}/tokens")
async def get_network_tokens(
    network_id: str,
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)"),
    page: Optional[int] = Query(1, description="Page number for pagination")
):
    """
    Get tokens for a specific blockchain network
    """
    try:
        params = {
            "page": page,
            "limit": limit
        }
        result = await fetch_from_geckoterminal(f"/networks/{network_id}/tokens", params)
        return result
    except Exception as e:
        print(f"Error in get_network_tokens: {str(e)}")
        raise

# Additional endpoints from previous implementation can be added here

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8089))  # Use PORT from environment or default to 8089
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting GeckoTerminal API server on {host}:{port}")
    
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=True  # Enable auto-reload for development
    )
