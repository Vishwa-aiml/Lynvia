import pytest


def register_designer_and_setup(client, email, password, headline, rate, years, skill_names=None, service_category=None):
    # register and login
    data = {"email": email, "password": password, "role": "DESIGNER", "full_name": "D"}
    r = client.post("/auth/register", json=data)
    assert r.status_code in (200, 201)
    r = client.post("/auth/login", json={"email": email, "password": password})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    # create profile
    r = client.post("/profiles/designer", json={"headline": headline, "hourly_rate": rate, "years_experience": years}, headers=headers)
    assert r.status_code in (200,201), f"profile create failed: {r.status_code} {r.text}"
    # add service
    if service_category:
        r2 = client.post("/services", json={"title": "Svc", "category": service_category, "price": 1000, "delivery_days": 3}, headers=headers)
        assert r2.status_code in (200,201), f"service create failed: {r2.status_code} {r2.text}"
    # add skills via services endpoint create_skill
    if skill_names:
        for s in skill_names:
            r3 = client.post("/services/skills", json={"name": s}, headers=headers)
            assert r3.status_code in (200,201), f"skill create failed: {r3.status_code} {r3.text}"
    return headers


def test_discover_by_skill_and_rate(client):
    headers1 = register_designer_and_setup(client, "disc1@example.com", "Pass1234!", "D1", 2000, 5, skill_names=["logo"], service_category="branding")
    headers2 = register_designer_and_setup(client, "disc2@example.com", "Pass1234!", "D2", 5000, 8, skill_names=["web"], service_category="web")

    # search for logo skill
    r = client.get("/discovery/designers?skills=logo&min_rate=1000&max_rate=3000")
    assert r.status_code == 200
    data = r.json()
    assert any(d["headline"] == "D1" for d in data)

    # search by category
    r2 = client.get("/discovery/designers?category=web")
    assert r2.status_code == 200
    data2 = r2.json()
    assert any(d["headline"] == "D2" for d in data2)
