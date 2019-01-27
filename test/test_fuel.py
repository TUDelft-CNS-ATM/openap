from openap import FuelFlow

ff = FuelFlow('C550', 'JT15D-4')

ff.plot_model()

def test_all():
    assert round(ff.at_thrust_ratio(0.1), 4) == 0.0305
    assert round(ff.at_thrust_ratio(0.9), 4) == 0.1521
