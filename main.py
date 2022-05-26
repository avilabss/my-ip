import aiohttp

from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseSettings, ValidationError


# Setting environment variables
class Settings(BaseSettings):
    ip_info_api_token: str

try:
    settings = Settings()
    ip_info_features = True
except ValidationError:
    ip_info_features = False
    print("Set IP_INFO_API_TOKEN in env before running to get full feature support")


# Init fastapi
app = FastAPI()


# Private methods
async def _get_ip_details(client_host: str) -> dict:
    url = f"https://ipinfo.io/{client_host}/json?token={settings.ip_info_api_token}"

    async with aiohttp.ClientSession() as sess:
        res = await sess.get(url)
        res_json = await res.json()

    return res_json


async def _get_full_ip_details(client_host: str) -> dict:
    url = f"https://ipinfo.io/widget/demo/{client_host}"
    headers = {"referer": "https://ipinfo.io/"}

    async with aiohttp.ClientSession(headers=headers) as sess:
        res = await sess.get(url)
        res_json = await res.json()

    return res_json


# Route handlers
@app.get("/")
async def root(request: Request):
    client_host = request.client.host
    return {"ip": client_host}


@app.get("/ping")
async def ping():
    return {"message": "pong!"}


@app.get("/detail")
async def my_ip_details(request: Request):
    client_host = request.client.host

    if not ip_info_features:
        raise HTTPException(status_code=404, detail="Failed to get ip details")

    try:
        ip_details = await _get_ip_details(client_host)
        return ip_details
    except:
        raise HTTPException(status_code=404, detail="Failed to get ip details")


@app.get("/detail/{ip}")
async def ip_details(ip: str):
    if not ip_info_features:
        raise HTTPException(status_code=404, detail="Failed to get ip details")

    if len(ip.split(".")) != 4 and len(ip.split(":")) != 8:
        raise HTTPException(status_code=404, detail="Invalid ip address")

    try:
        ip_details = await _get_ip_details(ip)
        return ip_details
    except:
        raise HTTPException(status_code=404, detail="Failed to get ip details")


@app.get("/full-detail")
async def my_ip_full_details(request: Request):
    client_host = request.client.host

    try:
        ip_details = await _get_full_ip_details(client_host)
        return ip_details
    except:
        raise HTTPException(status_code=404, detail="Failed to get full ip details")


@app.get("/full-detail/{ip}")
async def ip_full_details(ip: str):
    if len(ip.split(".")) != 4 and len(ip.split(":")) != 8:
        raise HTTPException(status_code=404, detail="Invalid ip address")

    try:
        ip_details = await _get_full_ip_details(ip)
        return ip_details
    except:
        raise HTTPException(status_code=404, detail="Failed to get full ip details")
