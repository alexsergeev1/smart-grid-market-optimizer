import pandas as pd
import streamlit as st
from optimizer import dispatch

st.set_page_config(page_title="Grid Market Optimizer", layout="wide")
st.title("Smart Grid & Energy Market Optimizer")
st.caption("Two-bus economic dispatch · Synthetic inputs · No real utility data")
with st.sidebar:
    st.header("Grid controls")
    demand = st.slider("Demand at Bus B (MW)", 20, 130, 80, 5)
    line = st.slider("Transmission capacity (MW)", 0, 120, 55, 5)
    solar = st.slider("Solar available at Bus A (MW)", 0, 35, 35, 5)
@st.cache_data(show_spinner=False)
def solve(d, l, s):
    return dispatch(d, l, s)
def fast_cost(d, l, s):
    imported = min(d, l, s + 70)
    local = d - imported
    if local > 80:
        return None
    solar_used = min(s, imported)
    gas_used = imported - solar_used
    return 5 * solar_used + 30 * gas_used + 115 * local
try:
    x = solve(demand, line, solar)
except ValueError as e:
    st.error(str(e))
    st.stop()
no_congestion = solve(demand, max(demand, 105), solar)
premium = x["cost_usd_per_hour"] - no_congestion["cost_usd_per_hour"]
st.caption(f"Current inputs: {demand} MW demand · {line} MW line · {solar} MW solar")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Operating cost", f'${x["cost_usd_per_hour"]:,.0f}/h')
m2.metric("Congestion premium", f'${premium:,.0f}/h')
m3.metric("Transmission flow", f'{x["flow_mw"]:,.0f} MW')
m4.metric("Bus B marginal price", f'${x["price_b_usd_mwh"]:,.0f}/MWh')
st.subheader("Optimal generation")
chart = pd.DataFrame({"Generator": ["Solar (A)", "Gas (A)", "Peaker (B)"], "MW": [x["solar_mw"], x["gas_mw"], x["peaker_mw"]]})
st.bar_chart(chart, x="Generator", y="MW", horizontal=True)
c1, c2 = st.columns(2)
with c1:
    st.subheader("Cost vs. line capacity")
    data = [{"Line capacity (MW)": cap, "Cost ($/h)": cost} for cap in range(0, 126, 5) if (cost := fast_cost(demand, cap, solar)) is not None]
    st.line_chart(pd.DataFrame(data), x="Line capacity (MW)", y="Cost ($/h)")
with c2:
    st.subheader("Marginal prices")
    st.bar_chart(pd.DataFrame({"Bus": ["A", "B"], "$/MWh": [x["price_a_usd_mwh"], x["price_b_usd_mwh"]]}), x="Bus", y="$/MWh")
st.subheader("Dispatch detail")
st.dataframe(chart, width="stretch", hide_index=True)
st.download_button("Download dispatch CSV", chart.to_csv(index=False), "dispatch.csv", "text/csv")
st.caption("Simplified two-bus linear dispatch, not AC power flow. AI forecasting and batteries are planned, not implemented.")
