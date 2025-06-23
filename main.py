from tkinter import *
import tkintermapview
import requests
from urllib.parse import quote

# === DANE CENTRÓW ===
centra = []
centrum_pracownicy = {}
centrum_klienci = {}

class CentrumHandlowe:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.latitude, self.longitude = self.get_coordinates()
        self.marker = map_widget.set_marker(self.latitude, self.longitude, text=self.nazwa)

    def get_coordinates(self):
        try:
            url = f"https://nominatim.openstreetmap.org/search.php?q={quote(self.nazwa)}&format=jsonv2"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            data = resp.json()
            return float(data[0]["lat"]), float(data[0]["lon"])
        except:
            return 52.23, 21.0
