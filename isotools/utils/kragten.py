from typing import Callable, List, Tuple
import numpy as np


def propagate_kragten(
    model_func: Callable[[List[float]], float],
    params: List[float],
    uncertainties: List[float],
) -> Tuple[float, float]:
    """
    Performs uncertainty propagation using the Kragten numerical differentiation method.

    Args:
        model_func: A function that accepts a list of float arguments and returns a float.
                    f([x1, x2, ...]) -> y
        params: List of nominal values [x1, x2, ...]
        uncertainties: List of standard uncertainties (1 sigma) [u1, u2, ...] for each param.

    Returns:
        (nominal_y, combined_uncertainty)
    """
    # 1. Calculate Nominal Value
    y0 = model_func(params)

    # 2. Sum of Squares for perturbations
    sum_squares = 0.0

    # We iterate over every parameter to calculate its partial derivative contribution
    for i, u_i in enumerate(uncertainties):
        if u_i == 0:
            continue

        # Create a perturbed parameter set: [x1, x2, ..., xi + ui, ...]
        # Note: Kragten suggests perturbing by u_i directly
        p_perturbed = params.copy()
        p_perturbed[i] += u_i

        y_p = model_func(p_perturbed)

        # dy = f(x+u) - f(x)
        dy = y_p - y0
        sum_squares += dy**2

    u_combined = np.sqrt(sum_squares)

    return y0, u_combined
