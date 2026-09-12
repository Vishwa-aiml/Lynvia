import pytest


def create_client_and_project(client, email="client@example.com"):
    # register client
    r = client.post("/auth/register", json={"email": email, "password": "Pass1234!", "role": "CLIENT", "full_name": "C"})
    assert r.status_code in (200,201)
    r = client.post("/auth/login", json={"email": email, "password": "Pass1234!"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    # create project
    proj = client.post("/projects", json={"title": "P1", "description": "X", "budget": 10000}, headers=headers)
    assert proj.status_code in (200,201), proj.text
    return headers, proj.json()["id"]


def create_designer(client, email="designer@example.com", headline="H", rate=2000):
    r = client.post("/auth/register", json={"email": email, "password": "Pass1234!", "role": "DESIGNER", "full_name": "D"})
    assert r.status_code in (200,201)
    r = client.post("/auth/login", json={"email": email, "password": "Pass1234!"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post("/profiles/designer", json={"headline": headline, "hourly_rate": rate, "years_experience": 3}, headers=headers)
    assert r.status_code in (200,201)
    # get current user id from /auth/me
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    user_id = me.json()["id"]
    # fetch the designer profile for this user
    prof = client.get(f"/profiles/designer/{user_id}")
    assert prof.status_code == 200
    profile = prof.json()
    return headers, profile["id"]


def test_invite_accept_flow(client):
    client_headers, project_id = create_client_and_project(client, email="invclient@example.com")
    designer_headers, designer_profile_id = create_designer(client, email="invdesigner@example.com")

    # client uses the known designer profile id
    designer_id = designer_profile_id

    # invite designer
    r = client.post(f"/projects/{project_id}/invite", json={"designer_id": designer_id, "message": "Please join"}, headers=client_headers)
    assert r.status_code in (200,201), r.text
    invitation = r.json()
    inv_id = invitation["id"]
    assert invitation["status"] == "pending"

    # designer lists their invitations
    r2 = client.get("/invitations/me", headers=designer_headers)
    assert r2.status_code == 200
    found = any(i["id"] == inv_id for i in r2.json())
    assert found

    # accept invitation
    r3 = client.post(f"/invitations/{inv_id}/accept", headers=designer_headers)
    assert r3.status_code == 200
    inv2 = r3.json()
    assert inv2["status"] == "accepted"

    # project should be assigned and in progress
    rproj = client.get(f"/projects/{project_id}")
    assert rproj.status_code == 200
    pj = rproj.json()
    assert pj["status"] == "in_progress"
    assert pj["assigned_designer_id"] == designer_id


def test_unauthorized_accept(client):
    client_headers, project_id = create_client_and_project(client, email="uclient@example.com")
    designer_headers, designer_profile_id = create_designer(client, email="udesigner@example.com")
    other_headers, other_profile_id = create_designer(client, email="otherdesigner@example.com")

    designer_id = designer_profile_id
    r = client.post(f"/projects/{project_id}/invite", json={"designer_id": designer_id, "message": "Join pls"}, headers=client_headers)
    inv_id = r.json()["id"]

    # other designer tries to accept
    r2 = client.post(f"/invitations/{inv_id}/accept", headers=other_headers)
    assert r2.status_code == 403
