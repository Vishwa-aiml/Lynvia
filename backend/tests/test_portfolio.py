import pytest


def register_and_login(client, email, password, role="CLIENT", full_name=None):
    data = {"email": email, "password": password, "role": role}
    if full_name:
        data["full_name"] = full_name
    r = client.post("/auth/register", json=data)
    assert r.status_code in (200, 201)
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    token = r.json().get("access_token")
    return token


def test_designer_portfolio_create_and_list(client):
    designer_email = "designer1@example.com"
    designer_pw = "Password123!"
    token = register_and_login(client, designer_email, designer_pw, role="DESIGNER")
    headers = {"Authorization": f"Bearer {token}"}

    # create designer profile
    resp = client.post("/profiles/designer", json={"headline": "Designer 1", "hourly_rate": 2000, "years_experience": 3}, headers=headers)
    assert resp.status_code == 201

    # create portfolio item with media
    payload = {
        "title": "Project Alpha",
        "description": "A sample portfolio item",
        "category": "branding",
        "is_public": True,
        "media": [
            {"filename": "image1.png", "url": "http://example.com/image1.png", "mime_type": "image/png"}
        ]
    }
    r = client.post("/portfolio/", json=payload, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Project Alpha"
    assert data["media"] and data["media"][0]["filename"] == "image1.png"

    # list public portfolio (no auth)
    resp2 = client.get(f"/portfolio/designer/1?public_only=true")
    assert resp2.status_code == 200
    items = resp2.json()
    assert len(items) >= 1


def test_portfolio_ownership(client):
    # create a designer and portfolio
    designer_email = "owner@example.com"
    designer_pw = "Password123!"
    dtoken = register_and_login(client, designer_email, designer_pw, role="DESIGNER")
    headers = {"Authorization": f"Bearer {dtoken}"}
    client.post("/profiles/designer", json={"headline": "Owner", "hourly_rate": 1000}, headers=headers)
    r = client.post("/portfolio/", json={"title": "Owner Item"}, headers=headers)
    assert r.status_code == 201
    item_id = r.json()["id"]

    # create a client user
    client_email = "someclient@example.com"
    client_pw = "Password123!"
    ctoken = register_and_login(client, client_email, client_pw, role="CLIENT")
    c_headers = {"Authorization": f"Bearer {ctoken}"}

    # client tries to delete designer's portfolio -> should be forbidden
    resp = client.delete(f"/portfolio/{item_id}", headers=c_headers)
    assert resp.status_code == 403

    # owner can delete
    resp2 = client.delete(f"/portfolio/{item_id}", headers=headers)
    assert resp2.status_code == 204
