from openap import Drag

drag = Drag(ac='A320')

print('-'*70)

D = drag.clean(mass=60000, tas=200, alt=20000)
print("drag.clean(mass=60000, tas=200, alt=20000)")
print(D)
print('-'*70)

D = drag.clean(mass=60000, tas=250, alt=20000)
print("drag.clean(mass=60000, tas=250, alt=20000)")
print(D)
print('-'*70)

D = drag.nonclean(mass=60000, tas=150, alt=1000, flap_angle=20, path_angle=10, landing_gear=False)
print("drag.nonclean(mass=60000, tas=150, alt=1000, flap_angle=20, path_angle=10, landing_gear=False)")
print(D)
print('-'*70)

D = drag.nonclean(mass=60000, tas=150, alt=200, flap_angle=20, path_angle=10, landing_gear=True)
print("drag.nonclean(mass=60000, tas=150, alt=1000, flap_angle=20, path_angle=10, landing_gear=True)")
print(D)
print('-'*70)


D = drag.clean(mass=[60000], tas=[200], alt=[20000])
print("drag.clean(mass=[60000], tas=[200], alt=[20000])")
print(D)
print('-'*70)

D = drag.nonclean(mass=[60000], tas=[150], alt=[200], flap_angle=[20])
print("drag.nonclean(mass=[60000], tas=[150], alt=[200], flap_angle=[20]")
print(D)
print('-'*70)
