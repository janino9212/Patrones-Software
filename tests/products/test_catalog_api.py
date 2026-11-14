def _create(client, code: str = "PROD-001", name: str = "Vacuna refrigerada", **extra):
    return client.post("/products", json={"code": code, "name": name, **extra})


def test_create_product_returns_201_and_lists_it(client):
    response = _create(client, category="Farmacéutico")

    assert response.status_code == 201
    assert response.json()["code"] == "PROD-001"
    listed = client.get("/products").json()
    assert [(p["code"], p["name"], p["category"]) for p in listed] == [
        ("PROD-001", "Vacuna refrigerada", "Farmacéutico")
    ]


def test_products_are_listed_ordered_by_code(client):
    _create(client, code="PROD-B")
    _create(client, code="PROD-A")

    assert [p["code"] for p in client.get("/products").json()] == ["PROD-A", "PROD-B"]


def test_duplicate_code_returns_409(client):
    _create(client)

    response = _create(client, name="Otro nombre")

    assert response.status_code == 409
    assert len(client.get("/products").json()) == 1


def test_code_with_spaces_or_empty_name_returns_422(client):
    assert _create(client, code="PROD 001").status_code == 422
    assert _create(client, name="").status_code == 422


def test_create_product_requires_a_session(anonymous_client):
    assert _create(anonymous_client).status_code == 401
