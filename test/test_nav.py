from openap import nav

def test_all():
    lat0 = 51.9898
    lon0 =  4.3753
    assert nav.cloest_fix(lat0, lon0) == ([51.965556, 4.382778, 'EH155'], 2744)

    assert nav.closest_airport(52.011, 4.357) == 'EHRD'
    assert nav.closest_airport(0, 0) == None
    assert nav.airport_data('AMS')['icao'] == 'EHAM'
    assert nav.airport_data('EHAM')['iata'] == 'AMS'
    assert nav.airport_data('LALALAND') == None
