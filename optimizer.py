from math import isfinite
from scipy.optimize import linprog

GENS = {
    "Solar": {"max_mw": 35.0, "cost": 5.0, "bus": "A"},
    "Gas": {"max_mw": 70.0, "cost": 30.0, "bus": "A"},
    "Peaker": {"max_mw": 80.0, "cost": 115.0, "bus": "B"},
}


def dispatch(demand_mw=80.0, line_mw=55.0, solar_mw=35.0):
    values = (demand_mw, line_mw, solar_mw)
    if any(not isinstance(v, (int, float)) or not isfinite(v) for v in values):
        raise ValueError("Inputs must be finite numbers")
    if demand_mw < 0 or line_mw < 0 or not 0 <= solar_mw <= 35:
        raise ValueError("Invalid demand, line capacity, or solar availability")

    result = linprog(
        c=[5, 30, 115, 0],
        A_eq=[[1, 1, 0, -1], [0, 0, 1, 1]],
        b_eq=[0, demand_mw],
        bounds=[(0, solar_mw), (0, 70), (0, 80), (0, line_mw)],
        method="highs",
    )
    if not result.success:
        raise ValueError("Demand cannot be met with these limits")

    solar, gas, peaker, flow = (max(0.0, float(v)) for v in result.x)
    price_a, price_b = (float(v) for v in result.eqlin.marginals)
    return {
        "demand_mw": float(demand_mw),
        "line_mw": float(line_mw),
        "solar_mw": solar,
        "gas_mw": gas,
        "peaker_mw": peaker,
        "flow_mw": flow,
        "cost_usd_per_hour": float(result.fun),
        "price_a_usd_mwh": price_a,
        "price_b_usd_mwh": price_b,
        "price_spread_usd_mwh": price_b - price_a,
    }
