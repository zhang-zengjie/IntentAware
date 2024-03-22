import numpy as np
from config.overtaking.functions import gen_bases, get_intension, lanes
from libs.bicycle_model import BicycleModel


Ts = 1    # The discrete sampling time Delta_t
l = 4       # The baseline value of the vehicle length
N = 15      # The control horizon
M = 100
R = np.array([[1e4, 0], [0, 1e-2]])

mode = 2    # Select intention mode: 
            # 0 for switching-lane OV 
            # 1 for constant-speed OV
            # 2 for speeding-up OV

np.random.seed(7)

# The assumed control mode of the obstacle vehicle (OV)
v = get_intension(N, mode)
B = gen_bases(l)

# Generate the PCE instance and the specification

ego = BicycleModel(Ts, name='ego')                  # Dynamic model of the ego vehicle (EV)
oppo = BicycleModel(Ts, useq=v, basis=B, pce=True, name='oppo')     # Dynamic model of the obstacle vehicle (OV)

ego.update_param(np.array([0, l, 1]))
oppo.update_param(np.array([0, l, 1]))

v0 = 10
# Initial position of the ego vehicle (EV)
e0 = np.array([0, lanes['fast'], 0, v0*1.33])
# Initial position of the obstacle vehicle (OV)            
o0 = np.array([2*v0, lanes['slow'], 0, v0])    