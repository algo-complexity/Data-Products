from ninja import NinjaAPI

from api.api import router as api_router

api = NinjaAPI()

api.add_router("/api/", api_router)
