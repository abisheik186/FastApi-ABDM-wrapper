from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import httpx
import uuid
import json
from datetime import datetime, timezone

app = FastAPI()

# Sample Settings (You can replace this with an actual database fetch)
class ABDMSettings(BaseModel):
    client_id: str
    client_secret: str
    auth_base_url: str

# Dependency to get ABDM settings, replace with actual DB call
def get_abdm_settings() -> ABDMSettings:
    # Replace this with your actual database logic
    return ABDMSettings(
        client_id="SBX_002612",
        client_secret="a55d9396-8846-44c8-b26e-81bef3ec9adc",
        auth_base_url="https://dev.abdm.gov.in/api/hiecm/gateway/v3/sessions"
    )

@app.post("/get_authorization_token")
async def get_authorization_token(settings: ABDMSettings = Depends(get_abdm_settings)):
    config_url = "/v3/sessions"
    auth_base_url = settings.auth_base_url.rstrip("/")
    url = auth_base_url
    
    payload = {
        "clientId": settings.client_id,
        "clientSecret": settings.client_secret,
        "grantType": "client_credentials"
    }
    
    request_id = str(uuid.uuid4())
    utcnow = datetime.now(timezone.utc)
    timestamp = utcnow.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    
    headers = {
        "Content-Type": "application/json",
        "REQUEST-ID": request_id,
        "TIMESTAMP": timestamp,
        "X-CM-ID": "sbx"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        # Raise an exception if the status is not 2xx
        response.raise_for_status()

        # Parse the JSON response
        response_json = response.json()

        return {
            "accessToken": response_json.get("accessToken"),
            "tokenType": response_json.get("tokenType"),
            "status": "Granted"
        }

    except httpx.HTTPStatusError as exc:
        # Return a detailed error message
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error occurred: {exc}")
    
    except Exception as e:
        # Log and return a generic error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/api/v3/hip/token/on-generate-token")
async def handle_generate_token(request: Request):
    # Process the incoming data
    data = await request.json()
    return data
