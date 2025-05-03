import requests
from app.core.config import settings
from app.models import Location

class GeocodingService:
    def __init__(self):
        # use open-meteo geocoding api temporarily
        # can't search preceise addresses only cities
        self.url = settings.OPEN_METEO_API_URL

    def get_location(self, city: str) -> Location:
        resp = requests.get(self.url, params={'name': city, 'count': 1}) # just return the first result
        loc = resp.json()['results'][0]
        return Location(
            latitude=loc['latitude'],
            longitude=loc['longitude'],
            name=loc['name']
        )
