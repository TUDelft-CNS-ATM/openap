import requests
import json
import pandas as pd

url_airports = "http://www.flightradar24.com/_json/airports.php"

s = requests.Session()
s.headers.update({'user-agent': 'Mozilla/5.0'})

r = s.get(url_airports)

if r.status_code != 200:
    raise RuntimeError("Can not fetch FR24 source url!")

try:
    res = r.json()
except:
    raise RuntimeError("Source data format unknown")

if not res['rows']:
    raise RuntimeError("No infomation in the data")

df = pd.DataFrame(res['rows'])

df = df[['iata', 'icao', 'lat', 'lon', 'alt', 'country', 'name']]

df = df.sort_values('iata')

df.to_csv('db/airports.csv', index=False, encoding='utf-8')
