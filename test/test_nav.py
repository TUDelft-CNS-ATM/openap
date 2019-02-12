from openap import nav

print(nav.airport('Eham'))
print(nav.closest_airport(52.011, 4.357))

print(nav.fix('eh155'))
print(nav.closest_fix(52.011, 4.357))

def test_all():
    assert nav.airport('ams')['icao'] == 'EHAM'
    assert nav.airport('Eham')['iata'] == 'AMS'
    assert nav.airport('LALALAND') == None
    assert nav.closest_airport(52.011, 4.357) == 'EHRD'
    assert nav.closest_airport(0, 0) == None

    assert nav.fix('eh155') == [51.965556, 4.382778, 'EH155']
    assert nav.closest_fix(52.011, 4.357) == ([51.965556, 4.382778, 'EH155'], 2744)
