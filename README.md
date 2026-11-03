# Smart Grid & Energy Market Optimizer

A Python linear-optimization prototype that minimizes electricity generation cost while respecting generator and transmission limits.

**Status:** Version 1: economic dispatch and interactive visualization. AI forecasting, battery scheduling, and full network power-flow modeling are planned, **not yet implemented**.

## What it demonstrates

A synthetic two-bus grid with solar and gas power at Bus A, a peaker plant and demand at Bus B, and one limited transmission connection. The app determines which generators should operate and how much energy flows across the link. All units and prices are synthetic, not PECO/PJM measurements.

| Default scenario | Result |
| --- | ---: |
| Demand | 80 MW |
| Line capacity | 55 MW |
| Optimal dispatch | 35 MW solar + 20 MW gas + 25 MW peaker |
| Operating cost | $3,650 per hour |
| Cost without congestion | $1,525 per hour |
| Congestion premium | $2,125 per hour |
| Bus A / Bus B marginal prices | $30 / $115 per MWh |

**Why it matters:** A binding transmission limit forces the system to run more expensive local generation, increasing operating cost and creating a difference in marginal prices.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Technical approach

- Linear programming with `scipy.optimize.linprog` (HiGHS)
- Generation bounds, two energy-balance equations, transmission bound
- Marginal prices from linear-program equality constraint dual values
- Streamlit controls and sensitivity plots; pytest tests

## Limitations and roadmap

This is a **two-node transportation-style dispatch model**, not DC/AC optimal power flow. It ignores voltage, reactive power, ramp limits, outages, losses, and battery state-of-charge. The financial results represent **simulated operating costs**, not revenues or realized market outcomes.

Next: 3+ bus DC-OPF with Kirchhoff's laws; battery optimization; weather/load forecasting evaluated against simple baselines; real public PJM data with attribution.

References for further engineering extensions: [PyPSA examples](https://docs.pypsa.org/latest/examples/examples/).
