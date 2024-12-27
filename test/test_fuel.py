# %%
from openap import FuelFlow

fuel = FuelFlow(ac="a320", eng="cfm56-5b4")

print("-" * 70)
FF = fuel.at_thrust(acthr=50000, alt=0)
print("fuel.at_thrust(acthr=50000, alt=0)")
print(FF)
print("-" * 70)

FF = fuel.at_thrust(acthr=50000, alt=20000)
print("fuel.at_thrust(acthr=50000, alt=20000)")
print(FF)
print("-" * 70)

FF = fuel.takeoff(tas=100, alt=0, throttle=1)
print("fuel.takeoff(tas=100, alt=0, throttle=1)")
print(FF)
print("-" * 70)

FF = fuel.enroute(mass=60000, tas=200, alt=20000, vs=1000)
print("fuel.enroute(mass=60000, tas=200, alt=20000, vs=1000)")
print(FF)
print("-" * 70)

FF = fuel.enroute(mass=60000, tas=230, alt=32000, vs=0)
print("fuel.enroute(mass=60000, tas=230, alt=32000, vs=0)")
print(FF)
print("-" * 70)

FF = fuel.enroute(mass=[60000], tas=[230], alt=[32000], vs=[0])
print("fuel.enroute(mass=[60000], tas=[230], alt=[32000], vr=[0])")
print(FF)
print("-" * 70)
