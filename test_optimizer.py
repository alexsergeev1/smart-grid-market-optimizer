import pytest
from optimizer import dispatch


def test_congested_grid():
    x = dispatch()
    assert x["solar_mw"] == pytest.approx(35)
    assert x["gas_mw"] == pytest.approx(20)
    assert x["peaker_mw"] == pytest.approx(25)
    assert x["flow_mw"] == pytest.approx(55)
    assert x["cost_usd_per_hour"] == pytest.approx(3650)


def test_uncongested_grid():
    x = dispatch(line_mw=120)
    assert x["solar_mw"] == pytest.approx(35)
    assert x["gas_mw"] == pytest.approx(45)
    assert x["peaker_mw"] == pytest.approx(0)
    assert x["cost_usd_per_hour"] == pytest.approx(1525)


def test_congestion_increases_cost():
    assert dispatch()["cost_usd_per_hour"] > dispatch(line_mw=120)["cost_usd_per_hour"]


def test_prices():
    x = dispatch()
    assert x["price_a_usd_mwh"] == pytest.approx(30)
    assert x["price_b_usd_mwh"] == pytest.approx(115)
    assert x["price_spread_usd_mwh"] == pytest.approx(85)


def test_balance():
    for demand, line, solar in [(70, 45, 20), (80, 55, 35), (100, 70, 25)]:
        x = dispatch(demand, line, solar)
        assert x["solar_mw"] + x["gas_mw"] + x["peaker_mw"] == pytest.approx(demand)
        assert x["flow_mw"] <= line + 1e-8


@pytest.mark.parametrize("args", [(140, 55, 35), (-1, 55, 35), (80, -1, 35), (80, 55, 40), (float("nan"), 55, 35)])
def test_invalid_or_infeasible(args):
    with pytest.raises(ValueError):
        dispatch(*args)
