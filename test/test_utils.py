from openap import utils
import pprint

pprint.pprint(utils.get_aircraft('A320'))
pprint.pprint(utils.get_dragpolar('A320'))
pprint.pprint(utils.get_airport_data('AMS'))
pprint.pprint(utils.get_engine('CFM56-5B4'))
# pprint.pprint(utils.get_engine('JT15D-4'))

def test_all():
    assert utils.get_closest_airport(52.011, 4.357) == 'EHRD'
    assert utils.get_closest_airport(0, 0) == None
    assert utils.get_airport_data('AMS')['icao'] == 'EHAM'
    assert utils.get_airport_data('EHAM')['iata'] == 'AMS'
    assert utils.get_airport_data('LALALAND') == None
    assert utils.get_engine('JT15D-4')['uid'] == '1PW036'
