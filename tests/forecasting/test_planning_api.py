def _record(client, product_id: str, period: str, quantity: float):
    return client.post(
        "/forecasting/demand",
        json={"product_id": product_id, "period": period, "quantity": quantity},
    )


def _seed_history(client, product_id: str, quantities: list[float]) -> None:
    for month, quantity in enumerate(quantities, start=1):
        assert _record(client, product_id, f"2026-{month:02d}-01", quantity).status_code == 201


def _command(client, action: str, product_id: str, model: str | None = None):
    payload = {"action": action, "product_id": product_id}
    if model:
        payload["model"] = model
    return client.post("/forecasting/commands", json=payload)


def test_demand_records_are_listed_by_period(client):
    _record(client, "P-api", "2026-03-01", 30)
    _record(client, "P-api", "2026-01-01", 10)

    body = client.get("/forecasting/demand/P-api").json()

    assert [(item["period"], item["quantity"]) for item in body] == [
        ("2026-01-01", 10.0),
        ("2026-03-01", 30.0),
    ]


def test_recording_the_same_period_twice_corrects_the_quantity(client):
    _record(client, "P-api", "2026-01-01", 10)
    _record(client, "P-api", "2026-01-01", 15)

    body = client.get("/forecasting/demand/P-api").json()

    assert [item["quantity"] for item in body] == [15.0]


def test_negative_demand_or_product_id_with_spaces_returns_422(client):
    assert _record(client, "P-api", "2026-01-01", -1).status_code == 422
    assert _record(client, "P api", "2026-01-01", 5).status_code == 422


def test_models_endpoint_lists_the_three_models(client):
    names = [model["name"] for model in client.get("/forecasting/models").json()]

    assert names == ["moving_average", "exponential_smoothing", "linear_trend"]


def test_plan_of_product_without_forecast_returns_404(client):
    assert client.get("/forecasting/plans/P-nada").status_code == 404


def test_generate_recalculate_and_undo_flow(client):
    _seed_history(client, "P-flow", [10, 20, 30])

    generated = _command(client, "generate", "P-flow")
    assert generated.status_code == 200
    assert generated.json()["predicted_demand"] == 20.0
    assert generated.json()["can_undo"] is True

    recalculated = _command(client, "recalculate", "P-flow", "linear_trend")
    assert recalculated.json()["predicted_demand"] == 40.0
    assert client.get("/forecasting/plans/P-flow").json()["model"] == "linear_trend"

    undone = client.post("/forecasting/commands/undo", json={"product_id": "P-flow"})
    assert undone.status_code == 200
    assert undone.json()["plan"]["model"] == "moving_average"
    assert undone.json()["plan"]["predicted_demand"] == 20.0

    undone_again = client.post("/forecasting/commands/undo", json={"product_id": "P-flow"})
    assert undone_again.json()["plan"] is None
    assert client.get("/forecasting/plans/P-flow").status_code == 404

    nothing_left = client.post("/forecasting/commands/undo", json={"product_id": "P-flow"})
    assert nothing_left.status_code == 409


def test_generate_without_history_returns_400(client):
    response = _command(client, "generate", "P-vacio")

    assert response.status_code == 400
    assert "al menos" in response.json()["detail"]


def test_generate_twice_and_recalculate_without_plan_return_409(client):
    _seed_history(client, "P-conf", [5, 6])

    assert _command(client, "recalculate", "P-conf").status_code == 409
    assert _command(client, "generate", "P-conf").status_code == 200
    assert _command(client, "generate", "P-conf").status_code == 409


def test_unknown_action_or_model_returns_422(client):
    assert _command(client, "borrar", "P-x").status_code == 422
    assert _command(client, "generate", "P-x", "red_neuronal").status_code == 422


def test_command_log_lists_operations_newest_first(client):
    _seed_history(client, "P-log", [5, 6])
    _command(client, "generate", "P-log")
    _command(client, "recalculate", "P-log")

    log = client.get("/forecasting/commands").json()

    assert [(entry["command"], entry["product_id"]) for entry in log] == [
        ("recalculate", "P-log"),
        ("generate", "P-log"),
    ]


def test_report_uses_the_plan_when_the_product_has_one(client, auth_headers):
    _seed_history(client, "P-rep", [10, 20, 30])
    before = client.get("/forecasting/reports/P-rep", headers=auth_headers).json()
    _command(client, "generate", "P-rep", "linear_trend")

    after = client.get("/forecasting/reports/P-rep", headers=auth_headers).json()

    assert (before["source"], before["predicted_demand"]) == ("eventos_tracking", 0.0)
    assert (after["source"], after["predicted_demand"]) == ("linear_trend", 40.0)
    assert after["confidence_interval"] == [36.0, 44.0]
