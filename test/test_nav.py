from openap import nav

def test_all():
    lat0 = 51.9898
    lon0 =  4.3753
    assert nav.get_cloest_fix(lat0, lon0) == ([51.965556, 4.382778, 'EH155'], 2744)
