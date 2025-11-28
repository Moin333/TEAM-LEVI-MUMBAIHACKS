from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(None)):
    """Simple API key verification (optional)"""
    # For now, allow all requests
    # You can add authentication later
    return True