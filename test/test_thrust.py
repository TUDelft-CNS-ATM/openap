import pandas as pd
import numpy as np
from openap import utils
from openap import thrust
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

engs = utils.get_engines('V2500')
dfengs = pd.DataFrame.from_dict(engs, orient='index')
eng = dfengs.iloc[0]

TF2S = thrust.TF2S(eng.thr, eng.bpr)

print("Engine", eng['name'])
print("Maximum thrust", eng['thr'])
print("BPR", eng['bpr'])

fig = plt.figure(figsize=(10,8))

# ax = fig.add_subplot(121)
# tas = np.arange(0, 200, 10)
#
# thr1 = TF2S.takeoff(tas)
# thr2 = TF2S.takeoff(tas, alt=500)
#
# ax.plot(tas, thr1, label='alt=0')
# ax.plot(tas, thr2, label='alt=500 ft')
# ax.legend()

ax = fig.add_subplot(111, projection='3d')

tas = np.arange(0, 500, 20)
alt = np.arange(0, 35000, 2000)
x, y = np.meshgrid(tas, alt)

thr_to = TF2S.takeoff(x, y) * 2
thr_cl = TF2S.inflight(x, y, 2000) * 2

c1, c2, c3 = .14231E+06, .51680E+05, .56809E-10
thr_bada = c1 * (1 - y / c2 + c3 * y**2)

plt.title('inflight')
ax.plot_wireframe(x, y, thr_to, color='r', label='TF2S-TO')
ax.plot_wireframe(x, y, thr_cl, color='g', label='TF2S-CL')
ax.plot_wireframe(x, y, thr_bada, color='b', label='BADA3')
ax.set_xlabel('tas (kts)')
ax.set_ylabel('alt (ft)')
ax.set_zlabel('thr (N)')
ax.view_init(20, 40)
ax.set_zlim([0, np.max(thr_to)*1.1])
ax.legend()
plt.tight_layout()
plt.show()
