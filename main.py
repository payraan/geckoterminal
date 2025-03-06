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
    result = await fetch_from_geckoterminal("/networks/trending")
    
    # Limit the number of networks returned
    if "data" in result and isinstance(result["data"], list):
        result["data"] = result["data"][:min(limit, 100)]
    
    return result

# 2️⃣ Search for networks
@app.get("/networks/search")
async def search_networks(
    query: str = Query(..., description="Network name or ID to search for"),
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)")
):
    """
    Search for networks by name or ID
    """
    params = {"query": query}
    result = await fetch_from_geckoterminal("/networks/search", params)
    
    # Limit the number of networks returned
    if "data" in result and isinstance(result["data"], list):
        result["data"] = result["data"][:min(limit, 100)]
    
    return result

# 3️⃣ Get pools for a specific network
@app.get("/networks/{network_id}/pools")
async def get_network_pools(
    network_id: str,
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)"),
    page: Optional[int] = Query(1, description="Page number for pagination")
):
    """
    Get pools for a specific blockchain network
    """
    params = {
        "page": page,
        "limit": limit
    }
    return await fetch_from_geckoterminal(f"/networks/{network_id}/pools", params)

# 4️⃣ Get tokens for a specific network
@app.get("/networks/{network_id}/tokens")
async def get_network_tokens(
    network_id: str,
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)"),
    page: Optional[int] = Query(1, description="Page number for pagination")
):
    """
    Get tokens for a specific blockchain network
    """
    params = {
        "page": page,
        "limit": limit
    }
    return await fetch_from_geckoterminal(f"/networks/{network_id}/tokens", params)

# 5️⃣ Get top tokens by volume
@app.get("/networks/{network_id}/tokens/top")
async def get_top_tokens_by_volume(
    network_id: str,
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)"),
    period: Optional[str] = Query("h24", description="Time period (h1, h6, h24, d7)")
):
    """
    Get top tokens by trading volume for a specific network
    """
    params = {
        "limit": limit,
        "period": period
    }
    return await fetch_from_geckoterminal(f"/networks/{network_id}/tokens/top", params)

# 6️⃣ Get specific token details
@app.get("/networks/{network_id}/tokens/{token_address}")
async def get_token_details(
    network_id: str,
    token_address: str
):
    """
    Get detailed information about a specific token
    """
    return await fetch_from_geckoterminal(f"/networks/{network_id}/tokens/{token_address}")

# 7️⃣ Get pools for a specific token
@app.get("/networks/{network_id}/tokens/{token_address}/pools")
async def get_token_pools(
    network_id: str,
    token_address: str,
    limit: Optional[int] = Query(10, description="Number of results to return (max 100)"),
    page: Optional[int] = Query(1, description="Page number for pagination")
):
    """
    Get pools for a specific token on a network
    """
    params = {
        "page": page,
        "limit": limit
    }
    return await fetch_from_geckoterminal(f"/networks/{network_id}/tokens/{token_address}/pools", params)

# 8️⃣ Get supported networks
@app.get("/networks")
async def get_supported_networks(
    limit: Optional[int] = Query(100, description="Number of results to return")
):
    """
    Get a list of all supported networks
    """
    params = {"limit": limit}
    return await fetch_from_geckoterminal("/networks", params)

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8087))  # Using port 8087 to avoid conflicts with other APIs
    print(f"🚀 Starting GeckoTerminal API server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
