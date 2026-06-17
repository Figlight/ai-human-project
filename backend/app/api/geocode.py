import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import settings
from backend.app.models.schemas import ApiResponse

router = APIRouter()


class ReverseGeocodeRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/reverse", response_model=ApiResponse)
async def reverse_geocode(req: ReverseGeocodeRequest):
    if not settings.AMAP_KEY:
        return ApiResponse(data={
            "address": f"{req.latitude:.4f}, {req.longitude:.4f}",
            "raw": None,
        })

    location = f"{req.longitude},{req.latitude}"
    url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {"key": settings.AMAP_KEY, "location": location, "output": "JSON"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        data = resp.json()

    if data.get("status") == "1" and data.get("regeocode"):
        address = data["regeocode"].get("formatted_address", "")
        return ApiResponse(data={
            "address": address,
            "raw": {
                "province": data["regeocode"].get("addressComponent", {}).get("province", ""),
                "city": data["regeocode"].get("addressComponent", {}).get("city", ""),
                "district": data["regeocode"].get("addressComponent", {}).get("district", ""),
                "street": data["regeocode"].get("addressComponent", {}).get("streetNumber", {}).get("street", ""),
            },
        })

    return ApiResponse(data={
        "address": f"{req.latitude:.4f}, {req.longitude:.4f}",
        "raw": None,
    })
