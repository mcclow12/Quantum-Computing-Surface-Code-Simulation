import matplotlib.pyplot as plt
import numpy as np
from surface_code_ideal import surface_code_sim


def simulation_sweep(distances, probabilities, num_trials, 
                            error_mode, display_mode=False):
    distance_to_results = {}
    for d in distances:
        ps = []
        ys = []
        for p in probabilities:
            count = 0
            s = surface_code_sim(d, p, error_mode, display_mode)
            for trial in range(num_trials):
                count += s.simulate()
                s.reset()
            ps.append(p)
            y = count/num_trials
            ys.append(y)
            print(p)
        distance_to_results[d] = (ps, ys)
        print(d)
    return distance_to_results

def plot_simulation_sweep(distances, probabilities, num_trials, 
                                error_mode, display_mode=False):
    results_dict = simulation_sweep(distances, probabilities, num_trials, 
                                            error_mode, display_mode)
    plt.figure()
    for d in distances:
        ps, ys = results_dict[d]
        plt.plot(ps, ys, label='distance {}'.format(d))
    plt.yscale('log')
    plt.legend()
    plt.show()

distances = [3, 5, 7]
probabilities = np.linspace(0.1, 0.2, 11)
num_trials = 1000
error_mode = 'depolarizing'
plot_simulation_sweep(distances, probabilities, num_trials, error_mode)



