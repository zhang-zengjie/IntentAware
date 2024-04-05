import numpy as np
from config import initialize
import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root)

from commons.pce_micp_solver import PCEMICPSolver

def main(scene):    

    N = 15      # Control horizon
    
    dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))    # The directory to save data

    print("---------------------------------------------------------")
    print('Initializing...')
    print("---------------------------------------------------------")
    # Initialize system and specification
    agents, phi = initialize(scene, N)
                # agents: the dictionary of agents (vehicles)
                    # agents['ego']: ego vehicle (EV)
                    # agents['oppo']: opponent vehicle (OV)
                # phi: the task specification

    # Load the solver
    solver = PCEMICPSolver(phi, agents, N)
    runtime = np.zeros((N, ))
    u_opt = np.zeros((2, ))

    for i in range(N):
        
        # Update the linearized matrices
        solver.agents['ego'].update_matrices(i)
        solver.agents['oppo'].update_matrices(i)

        # Update the linearized prediction
        solver.agents['oppo'].predict(i, N)
        
        # Update the dynamics constraints
        solver.AddDynamicsConstraints(i)

        # Update the cost
        solver.cost = 0.0
        solver.AddRobustnessConstraint()
        solver.AddQuadraticCost(i)

        # Solve the problem
        x, u, rho, runtime[i] = solver.Solve()
                    # x: the state decision variables
                    # u: the control decision variables
                    # rho: the specification satisfaction variable

        # Remove old dynamics constraints
        solver.RemoveDynamicsConstraints()

        # In case infeasibility, use the previous control input
        if (rho is not None) & (rho >=0):
            u_opt = u[:, i]

        # Apply the control input
        solver.agents['ego'].apply_control(i, u_opt)
        solver.agents['oppo'].apply_control(i, solver.agents['oppo'].useq[:, i])

    # Save data
    np.save(dir + '/xe_scene_' + str(scene) + '.npy', solver.agents['ego'].states)
    np.save(dir + '/xo_scene_' + str(scene) + '.npy', solver.agents['oppo'].pce_coefs)
    np.save(dir + '/run_time_' + str(scene) + '.npy', runtime)

    print("---------------------------------------------------------")
    print('Data saved to ' + dir)
    print("---------------------------------------------------------")


if __name__ == "__main__":

    # First of first, choose the mode
    intent = 1    # Select the intent of OV: 
                # 0 for switching-lane
                # 1 for slowing-down
                # 2 for speeding-up
    main(intent)