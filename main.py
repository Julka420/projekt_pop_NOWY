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

class Osoba:
    def __init__(self, imie_nazwisko, miasto, nazwa_centrum):
        self.imie_nazwisko = imie_nazwisko
        self.miasto = miasto
        self.nazwa_centrum = nazwa_centrum
        self.latitude, self.longitude = self.get_coordinates()
        self.marker = None

    def get_coordinates(self):
        try:
            url = f"https://nominatim.openstreetmap.org/search.php?q={quote(self.miasto)}&format=jsonv2"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            data = resp.json()
            return float(data[0]["lat"]), float(data[0]["lon"])
        except:
            return 52.23, 21.0

class Pracownik(Osoba): pass
class Klient(Osoba): pass

def otworz_panel_osob(nazwa_typu, typ_klasy, baza_danych):
    idx = listbox_centra.curselection()
    if not idx:
        return
    centrum = centra[idx[0]]
    nazwa_centrum = centrum.nazwa
    if nazwa_centrum not in baza_danych:
        baza_danych[nazwa_centrum] = []

    okno = Toplevel(root)
    okno.title(f"{nazwa_typu} – {nazwa_centrum}")
    okno.geometry("400x550")

    listbox = Listbox(okno, width=50, height=15)
    listbox.pack()

    def odswiez():
        listbox.delete(0, END)
        for i, o in enumerate(baza_danych[nazwa_centrum]):
            listbox.insert(i, f"{i+1}. {o.imie_nazwisko} – {o.miasto}")

    def dodaj():
        imie = entry_imie.get().strip()
        miasto = entry_miasto.get().strip()
        if not imie or not miasto:
            return
        osoba = typ_klasy(imie, miasto, nazwa_centrum)
        baza_danych[nazwa_centrum].append(osoba)
        odswiez()
        entry_imie.delete(0, END)
        entry_miasto.delete(0, END)

    def usun():
        sel = listbox.curselection()
        if not sel:
            return
        i = sel[0]
        if baza_danych[nazwa_centrum][i].marker:
            baza_danych[nazwa_centrum][i].marker.delete()
        baza_danych[nazwa_centrum].pop(i)
        odswiez()

    def edytuj():
        sel = listbox.curselection()
        if not sel:
            return
        i = sel[0]
        osoba = baza_danych[nazwa_centrum][i]
        entry_imie.delete(0, END)
        entry_imie.insert(0, osoba.imie_nazwisko)
        entry_miasto.delete(0, END)
        entry_miasto.insert(0, osoba.miasto)
        button_dodaj.config(text="Zapisz", command=lambda: zapisz(i))

    def zapisz(i):
        imie = entry_imie.get().strip()
        miasto = entry_miasto.get().strip()
        if not imie or not miasto:
            return
        if baza_danych[nazwa_centrum][i].marker:
            baza_danych[nazwa_centrum][i].marker.delete()
        baza_danych[nazwa_centrum][i] = typ_klasy(imie, miasto, nazwa_centrum)
        odswiez()
        entry_imie.delete(0, END)
        entry_miasto.delete(0, END)
        button_dodaj.config(text=f"Dodaj {nazwa_typu.lower()}", command=dodaj)

    def pokaz_na_mapie_wszystkich():
        osoby = baza_danych[nazwa_centrum]
        if not osoby:
            return
        for o in osoby:
            if o.marker:
                o.marker.delete()
            o.marker = map_widget.set_marker(o.latitude, o.longitude, text=f"{o.imie_nazwisko}\n({o.miasto})")
        lat = sum(o.latitude for o in osoby) / len(osoby)
        lon = sum(o.longitude for o in osoby) / len(osoby)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(8)

    entry_imie = Entry(okno, width=40)
    entry_imie.pack()
    entry_imie.insert(0, "Imię i nazwisko")

    entry_miasto = Entry(okno, width=40)
    entry_miasto.pack()
    entry_miasto.insert(0, "Miasto")

    button_dodaj = Button(okno, text=f"Dodaj {nazwa_typu.lower()}", command=dodaj)
    button_dodaj.pack(pady=2)

    Button(okno, text=f"Usuń {nazwa_typu.lower()}", command=usun).pack(pady=2)
    Button(okno, text=f"Edytuj {nazwa_typu.lower()}", command=edytuj).pack(pady=2)
    Button(okno, text="Pokaż wszystkich na mapie", command=pokaz_na_mapie_wszystkich).pack(pady=4)

    odswiez()
# === OPERACJE CENTRÓW ===
def dodaj_centrum():
    nazwa = entry_nazwa.get().strip()
    if not nazwa:
        return
    centrum = CentrumHandlowe(nazwa)
    centra.append(centrum)
    centrum_pracownicy[nazwa] = []
    centrum_klienci[nazwa] = []
    pokaz_centra()
    entry_nazwa.delete(0, END)
    entry_nazwa.focus()

def pokaz_centra():
    listbox_centra.delete(0, END)
    for i, centrum in enumerate(centra):
        listbox_centra.insert(i, f"{i+1}. {centrum.nazwa}")

def pokaz_na_mapie():
    idx = listbox_centra.curselection()
    if not idx:
        return
    centrum = centra[idx[0]]
    map_widget.set_position(centrum.latitude, centrum.longitude)
    map_widget.set_zoom(13)

def pokaz_wszystkie_centra_na_mapie():
    for c in centra:
        if c.marker:
            c.marker.delete()
        c.marker = map_widget.set_marker(c.latitude, c.longitude, text=c.nazwa)
    if centra:
        lat = sum(c.latitude for c in centra) / len(centra)
        lon = sum(c.longitude for c in centra) / len(centra)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(6)

def pokaz_osoby_centrum(typ_osoby):
    idx = listbox_centra.curselection()
    if not idx:
        return
    centrum = centra[idx[0]]
    nazwa = centrum.nazwa
    dane = centrum_pracownicy if typ_osoby == "pracownik" else centrum_klienci
    osoby = dane.get(nazwa, [])
    for o in osoby:
        if o.marker:
            o.marker.delete()
        o.marker = map_widget.set_marker(o.latitude, o.longitude, text=f"{o.imie_nazwisko}\n({o.miasto})")
    if osoby:
        lat = sum(o.latitude for o in osoby) / len(osoby)
        lon = sum(o.longitude for o in osoby) / len(osoby)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(7)
