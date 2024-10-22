from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import uuid
import json
from datetime import datetime, timezone
import logging

logging.basicConfig(filename = "app.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Sample Settings (You can replace this with an actual database fetch)
class ABDMSettings(BaseModel):
    client_id: str
    client_secret: str
    auth_base_url: str

class ABDMLinkTokenData (BaseModel):
    abhaAddress:str
    linkToken:str

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

@app.get("/")
async def read_root():
    logging.info("welcome")
    print("checking log...")
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/api/v3/hip/token/on-generate-token")
async def handle_generate_token(request:Request):
    print("inside handle generate token")
    logging.info("hello")
    try:
        data = await request.json()  # Attempt to get the JSON payload
        logging.info(f"Received data: {data}")
        print("data",data)
        response =  {
            "status":"success",
            "data": data
        }
        logging.info(f"Response data: {response}")
        return response,data
    except ValueError as ve:
        logging.error(f"Invalid JSON: {ve}")
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON", "error": str(ve)})
    except Exception as e:
        logging.error(f"Internal Server Error: {e}")
        print(f"Error: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")  # Raise an HTTP error

@app.post("/fetchlinktoken")
async def fetch_link_token():   
    url = "https://abdm-wrapper.onrender.com/api/v3/hip/token/on-generate-token"  # Replace with the actual URL
    async with httpx.AsyncClient() as client:
        response = await client.post(url)
        response_data = response.json()
        # link_token = response_data.get("linkToken")
        return response_data

from fastapi import FastAPI
import logging
from logging_config import setup_logging, send_to_slack

# Initialize FastAPI app
app = FastAPI()

# Set up logging
setup_logging()

@app.get("/test-logging")
async def test_logging():
    # Test: Info log
    logging.info("This is an INFO log test.")
    
    # Test: Send an info message directly to Slack
    send_to_slack("INFO: Testing direct Slack message functionality.")

    # Test: Warning log
    logging.warning("This is a WARNING log test.")

    # Test: Error log (will trigger Slack notification via logging)
    try:
        # Simulate an error
        1 / 0
    except ZeroDivisionError as e:
        logging.error(f"ERROR: Division by zero occurred: {e}")
        send_to_slack(f"ERROR: Division by zero detected: {e}")

    # Test: Critical log (will also trigger Slack notification)
    logging.critical("This is a CRITICAL log test.")

    # Test: Send custom data to Slack
    custom_data = {"status": "Testing", "message": "This is a custom data message for Slack."}
    send_to_slack(f"Custom Data: {custom_data}")

    return {"status": "Logging test completed. Check your Slack for logs."}
