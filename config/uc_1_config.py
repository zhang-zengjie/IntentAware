import numpy as np
import matplotlib.pyplot as plt
from libs.pce_basis import PCEBasis


lanes = {'right': 0,
         'slow': 2,
         'middle': 4,
         'fast': 6,
         'left': 8}


def gen_pce_specs(q, N, eta):

    B = PCEBasis(eta, q)        # Initialize the PCE instance

    eps = 0.05          # Probability threshold
    v_lim = 30          # Velocity limit

    # Coefficients of the predicates
    o = np.zeros((4, ))

    a1 = np.array([1, 0, 0, 0])
    a2 = np.array([0, 1, 0, 0])
    a3 = np.array([0, 0, 1, 0])
    a4 = np.array([0, 0, 0, 1])

    b = 5

    mu_safe = B.probability_formula(a1, -a1, 10, eps, name="oppo") | B.probability_formula(-a1, a1, 10, eps, name="oppo") | B.probability_formula(a2, -a2, 2, eps, name="oppo")

    mu_belief = B.variance_formula(a1, 20, name="oppo") & B.expectation_formula(o, -a2, -lanes['middle'], name="oppo") & B.expectation_formula(o, -a4, -v_lim, name="oppo")
    neg_mu_belief = B.neg_variance_formula(a1, 20, name="oppo") | B.expectation_formula(o, a2, lanes['middle'], name="oppo") | B.expectation_formula(o, a4, v_lim, name="oppo")

    mu_overtake = B.expectation_formula(a2, o, lanes['slow'] - 0.01, name="oppo") & B.expectation_formula(-a2, o, - lanes['slow'] - 0.011, name="oppo") \
                    & B.expectation_formula(a1, -a1, 2*b, name="oppo") \
                    & B.expectation_formula(a3, o, - 1e-6, name="oppo").always(0, 3) & B.expectation_formula(-a3, o, - 1e-6, name="oppo").always(0, 3) 

    phi_safe = mu_safe.always(0, N)
    phi_belief = mu_belief.always(0, N)
    phi_neg_belief = neg_mu_belief.eventually(0, N)
    phi_overtake = mu_overtake.eventually(0, N-3)

    phi = (phi_neg_belief | phi_overtake) & phi_safe

    return B, phi, B.expectation_formula(o, -a4, -v_lim, name="oppo").always(0, N)


def visualize(x, z0, v, B, bicycle_linear):

    from matplotlib.patches import Rectangle

    N = x.shape[1]-1
    N = 30
    H = 600

    plt.figure(figsize=(5,2))

    plt.plot(lanes['left'] * np.ones((H, )), linestyle='solid', linewidth=2, color='black')
    plt.plot(lanes['middle'] * np.ones((H, )), linestyle='dashed', linewidth=1, color='black')
    plt.plot(lanes['right'] * np.ones((H, )), linestyle='solid', linewidth=2, color='black')

    M = 64

    # Sample parameters from distribution eta
    nodes = B.eta.sample([M, ])

    mc_samples_linear = np.zeros([M, 4, N + 1])
    for i in range(M):
        bicycle_linear.update_initial(z0)
        bicycle_linear.update_parameter([nodes[0, i], nodes[1, i], 1])
        mc_samples_linear[i] = bicycle_linear.predict_linear(v, N)

    # Plot the trajectory of the ego vehicle (EV)
    tr1, = plt.plot(x[0, :], x[1, :], linestyle='solid', linewidth=2, color='red')
    p1, = plt.plot(x[0, -1], x[1, -1], alpha=0.8, color='red', marker="D", markersize=8)

    # Plot the trajectories of the obstacle vehicle (OV) 
    for i in range(M):
        tr2, = plt.plot(mc_samples_linear[i, 0, :], mc_samples_linear[i, 1, :], color=(0, 0, 0.5))
        # ax.add_patch(Rectangle(xy=(mc_samples_linear[i, -1, 0]-4, mc_samples_linear[i, -1, 1]-1) ,width=4, height=2, linewidth=1, color='blue', fill=False))
        p2, = plt.plot(mc_samples_linear[i, 0, -1]-4, mc_samples_linear[i, 1, -1], alpha=0.8, color=(0, 0, 0.5), marker="D", markersize=8)

    plt.xlim([0, H])
    plt.xlabel('x')
    plt.ylabel('y')
    # plt.legend([tr1, p1, tr2, p2], ['ego trajectory', 'ego position', 'obstacle trajectory', 'obstacle position'], loc='upper right', fontsize="10", ncol=2)

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    plt.show()