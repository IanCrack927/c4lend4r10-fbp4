import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import pytz

# --- CONFIGURACIÓN ---
# La URL general de los partidos de tu club
URL_CLUB = "https://www.fbpa.es/club-7731/partidos" 

# IMPORTANTE: Pon aquí el nombre EXACTO de tu equipo tal y como sale en la tabla
MI_EQUIPO = "C.B. L`ARBEYAL BLANCO"
# ---------------------

def obtener_partidos():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(URL_CLUB, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    c = Calendar()
    tz = pytz.timezone('Europe/Madrid')
    
    tablas = soup.find_all('table')
    
    for tabla in tablas:
        tbody = tabla.find('tbody')
        if not tbody:
            continue
            
        filas = tbody.find_all('tr')
        for fila in filas:
            celdas = fila.find_all('td')
            # Las tablas de Gesdeportiva suelen tener 7 columnas
            if len(celdas) >= 6:
                try:
                    fecha_str = celdas[1].text.strip()
                    hora_str = celdas[2].text.strip()
                    
                    # Saltar si no hay fecha o la hora no está definida
                    if not fecha_str or not hora_str or "def" in hora_str.lower():
                        continue
                        
                    local = celdas[3].text.strip()
                    visitante = celdas[4].text.strip()
                    # A veces la instalación está en la columna 6, a veces en la 5
                    pabellon = celdas[-1].text.strip() 
                    
                    # Filtrar: Si tu equipo no está en el partido, pasamos al siguiente
                    if MI_EQUIPO.lower() not in local.lower() and MI_EQUIPO.lower() not in visitante.lower():
                        continue
                        
                    # Convertir el texto a fecha real
                    dt_start = datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
                    dt_start = tz.localize(dt_start)
                    
                    # Crear el evento en el calendario
                    e = Event()
                    e.name = f"🏀 {local} vs {visitante}"
                    e.begin = dt_start
                    e.duration = {"hours": 1, "minutes": 30}
                    e.location = pabellon
                    
                    c.events.add(e)
                except Exception as e:
                    # Si falla una fila rara, que siga con las demás
                    continue
                    
    # Generar el archivo
    with open('partidos_fbpa.ics', 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
        
if __name__ == "__main__":
    obtener_partidos()
