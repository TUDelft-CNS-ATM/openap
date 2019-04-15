from openap import FuelFlow

fuel = FuelFlow(ac='A320', eng='CFM56-5B4')

print('-'*70)
FF = fuel.at_thrust(acthr=50000, alt=0)
print("fuel.at_thrust(acthr=50000, alt=0)")
print(FF)
print('-'*70)

FF = fuel.at_thrust(acthr=50000, alt=20000)
print("fuel.at_thrust(acthr=50000, alt=20000)")
print(FF)
print('-'*70)

FF = fuel.takeoff(tas=100, alt=0, throttle=1)
print("fuel.takeoff(tas=100, alt=0, throttle=1)")
print(FF)
print('-'*70)

FF = fuel.enroute(mass=60000, tas=200, alt=20000, path_angle=3)
print("fuel.enroute(mass=60000, tas=200, alt=20000, path_angle=3)")
print(FF)
print('-'*70)

FF = fuel.enroute(mass=60000, tas=230, alt=32000, path_angle=0)
print("fuel.enroute(mass=60000, tas=230, alt=32000, path_angle=0)")
print(FF)
print('-'*70)

FF = fuel.enroute(mass=[60000], tas=[230], alt=[32000], path_angle=[0])
print("fuel.enroute(mass=[60000], tas=[230], alt=[32000], path_angle=[0])")
print(FF)
print('-'*70)
