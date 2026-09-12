"""
tests/test_disputes.py — Disputes & Resolution system tests.

Covers:
  Authorization, state machine, financial resolution, ledger integrity,
  notifications, project events, regression checks.
"""
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.payment import PaymentStatus, EarningStatus, LedgerEntry
from app.models.dispute import DisputeStatus


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def register_and_login(client, email, password="pass1234!", role="CLIENT"):
    r = client.post("/auth/register", json={"email": email, "password": password, "full_name": "Test", "role": role})
    assert r.status_code == 201, r.json()
    tok = client.post("/auth/login", json={"email": email, "password": password})
    assert tok.status_code == 200, tok.json()
    token = tok.json()["access_token"]
    return r.json()["id"], token, {"Authorization": f"Bearer {token}"}


def register_admin(client, db, _suffix="default", password="admin1234!"):
    """Register + elevate an ADMIN user using the configured ADMIN_EMAIL.

    The test DB is wiped between tests so reusing the same email is safe.
    We MUST use settings.ADMIN_EMAIL so the updated require_admin_role
    email-check passes.
    """
    from app.core.config import settings as _settings
    email = _settings.ADMIN_EMAIL
    r = client.post("/auth/register", json={"email": email, "password": password, "full_name": "Admin", "role": "CLIENT"})
    # 400 means user already exists in this test (idempotent fallback)
    if r.status_code not in (200, 201):
        # User already created; just login
        pass
    from app.models.user import User, UserRole
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        # Registration succeeded
        user = db.query(User).filter(User.email == email).first()
    user.role = UserRole.ADMIN
    db.commit()
    tok = client.post("/auth/login", json={"email": email, "password": password})
    assert tok.status_code == 200, tok.json()
    token = tok.json()["access_token"]
    user_id = user.id
    return user_id, token, {"Authorization": f"Bearer {token}"}


def setup_project(client, db, suffix=""):
    c_id, c_tok, c_hdrs = register_and_login(client, f"dc_client{suffix}@test.com", role="CLIENT")
    d_id, d_tok, d_hdrs = register_and_login(client, f"dc_designer{suffix}@test.com", role="DESIGNER")
    dp = client.post("/profiles/designer", json={"bio": "bio", "hourly_rate": 5000}, headers=d_hdrs)
    assert dp.status_code in (200, 201), dp.json()
    dp_id = dp.json()["id"]

    proj = client.post("/projects/", json={"title": f"Proj {suffix}", "description": "d", "budget": 10000}, headers=c_hdrs)
    assert proj.status_code == 201, proj.json()
    project_id = proj.json()["id"]

    inv = client.post(f"/projects/{project_id}/invite", json={"designer_id": dp_id}, headers=c_hdrs)
    assert inv.status_code == 201, inv.json()
    inv_id = inv.json()["id"]

    acc = client.post(f"/invitations/{inv_id}/accept", headers=d_hdrs)
    assert acc.status_code == 200, acc.json()

    return project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id


def create_dispute(client, project_id, headers, reason="delivery_quality", description="The delivery is missing key elements from the brief."):
    r = client.post(
        f"/projects/{project_id}/disputes",
        json={"reason": reason, "description": description},
        headers=headers,
    )
    return r


# ─────────────────────────────────────────────────────────────────────────────
# 1. Creation and authorization
# ─────────────────────────────────────────────────────────────────────────────

def test_client_creates_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "cd1")
    r = create_dispute(client, project_id, c_hdrs)
    assert r.status_code == 201, r.json()
    assert r.json()["status"] == "open"
    assert r.json()["reason"] == "delivery_quality"


def test_designer_creates_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "cd2")
    # d_hdrs is at index 6 of setup_project return (project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id)
    r = create_dispute(client, project_id, d_hdrs, reason="out_of_scope_request",
                       description="Client is requesting work outside the original scope agreement.")
    assert r.status_code == 201, r.json()
    assert r.json()["raised_by_user_id"] == d_id


def test_unrelated_user_cannot_create_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "cd3")
    _, _, other_hdrs = register_and_login(client, "unrelated_cd3@test.com", role="CLIENT")
    r = create_dispute(client, project_id, other_hdrs)
    assert r.status_code == 400, r.json()


def test_unauthenticated_cannot_create_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "cd4")
    r = client.post(f"/projects/{project_id}/disputes", json={"reason": "other", "description": "x" * 20})
    assert r.status_code == 401, r.json()


def test_description_too_short_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "cd5")
    r = client.post(f"/projects/{project_id}/disputes",
                    json={"reason": "other", "description": "short"},
                    headers=c_hdrs)
    assert r.status_code == 422, r.json()


def test_invalid_reason_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "cd6")
    r = client.post(f"/projects/{project_id}/disputes",
                    json={"reason": "make_it_up", "description": "x" * 20},
                    headers=c_hdrs)
    assert r.status_code == 422, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Duplicate protection
# ─────────────────────────────────────────────────────────────────────────────

def test_duplicate_active_dispute_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "dup1")
    r1 = create_dispute(client, project_id, c_hdrs)
    assert r1.status_code == 201, r1.json()
    r2 = create_dispute(client, project_id, c_hdrs)
    assert r2.status_code == 400, r2.json()
    assert "active dispute" in r2.json()["detail"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 3. Get / list
# ─────────────────────────────────────────────────────────────────────────────

def test_participant_can_get_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "get1")
    r = create_dispute(client, project_id, c_hdrs)
    dispute_id = r.json()["id"]

    # Both parties can retrieve
    assert client.get(f"/disputes/{dispute_id}", headers=c_hdrs).status_code == 200
    assert client.get(f"/disputes/{dispute_id}", headers=d_hdrs).status_code == 200


def test_unrelated_user_cannot_get_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "get2")
    r = create_dispute(client, project_id, c_hdrs)
    dispute_id = r.json()["id"]
    _, _, other_hdrs = register_and_login(client, "other_get2@test.com", role="CLIENT")
    assert client.get(f"/disputes/{dispute_id}", headers=other_hdrs).status_code == 403


def test_list_project_disputes(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "list1")
    create_dispute(client, project_id, c_hdrs)
    r = client.get(f"/projects/{project_id}/disputes", headers=c_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["total"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# 4. Status transitions
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_can_move_to_under_review(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "st1")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_st1@test.com")
    r = client.patch(f"/disputes/{dispute_id}/status",
                     json={"status": "under_review"}, headers=admin_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "under_review"


def test_invalid_transition_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "st2")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_st2@test.com")
    # OPEN → RESOLVED is invalid (must go through UNDER_REVIEW first)
    r = client.patch(f"/disputes/{dispute_id}/status",
                     json={"status": "resolved"}, headers=admin_hdrs)
    assert r.status_code == 400, r.json()


def test_non_admin_cannot_change_status(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "st3")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    r = client.patch(f"/disputes/{dispute_id}/status",
                     json={"status": "under_review"}, headers=c_hdrs)
    assert r.status_code == 403, r.json()


def test_creator_can_cancel_own_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "st4")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    r = client.patch(f"/disputes/{dispute_id}/status",
                     json={"status": "cancelled"}, headers=c_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "cancelled"


def test_non_creator_cannot_cancel_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "st5")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    # Designer tries to cancel client's dispute
    r = client.patch(f"/disputes/{dispute_id}/status",
                     json={"status": "cancelled"}, headers=d_hdrs)
    assert r.status_code == 403, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Responses
# ─────────────────────────────────────────────────────────────────────────────

def test_valid_response(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "resp1")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    r = client.post(f"/disputes/{dispute_id}/responses",
                    json={"message": "Here is my side of the story with full context."},
                    headers=d_hdrs)
    assert r.status_code == 201, r.json()
    assert r.json()["user_id"] == d_id


def test_unauthorized_response_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "resp2")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    _, _, other_hdrs = register_and_login(client, "other_resp2@test.com", role="CLIENT")
    r = client.post(f"/disputes/{dispute_id}/responses",
                    json={"message": "I am not involved but trying anyway."},
                    headers=other_hdrs)
    assert r.status_code == 403, r.json()


def test_response_on_resolved_dispute_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "resp3")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_resp3@test.com")

    # Cancel (a terminal state)
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "cancelled"}, headers=c_hdrs)

    r = client.post(f"/disputes/{dispute_id}/responses",
                    json={"message": "Trying after cancellation."},
                    headers=c_hdrs)
    assert r.status_code == 400, r.json()


def test_list_responses(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "resp4")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    client.post(f"/disputes/{dispute_id}/responses",
                json={"message": "Client response here with sufficient context."},
                headers=c_hdrs)
    client.post(f"/disputes/{dispute_id}/responses",
                json={"message": "Designer rebuttal with full detail and evidence."},
                headers=d_hdrs)
    r = client.get(f"/disputes/{dispute_id}/responses", headers=c_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["total"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# 6. Admin resolution — NO_REFUND
# ─────────────────────────────────────────────────────────────────────────────

def test_non_admin_cannot_resolve(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "res1")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "no_refund",
                          "resolution_note": "No valid refund basis found after investigation."},
                    headers=c_hdrs)
    assert r.status_code == 403, r.json()


def test_admin_no_refund_resolution(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "res2")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_res2@test.com")

    # Put under review first
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "no_refund",
                          "resolution_note": "Investigation concluded no valid grounds for refund."},
                    headers=admin_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "resolved"
    assert r.json()["resolution_type"] == "no_refund"


def test_duplicate_resolution_prevented(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "res3")
    dispute_id = create_dispute(client, project_id, c_hdrs).json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_res3@test.com")
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)
    client.post(f"/disputes/{dispute_id}/resolve",
                json={"resolution_type": "no_refund",
                      "resolution_note": "No grounds found after thorough review."},
                headers=admin_hdrs)
    # Second resolve attempt
    r2 = client.post(f"/disputes/{dispute_id}/resolve",
                     json={"resolution_type": "no_refund",
                           "resolution_note": "Trying again after already resolved."},
                     headers=admin_hdrs)
    assert r2.status_code == 400, r2.json()


# ─────────────────────────────────────────────────────────────────────────────
# 7. Financial resolutions (require a succeeded payment)
# ─────────────────────────────────────────────────────────────────────────────

def _setup_project_with_payment(client, db, suffix):
    """Create a project with a mocked SUCCEEDED payment via DB injection."""
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, suffix)

    # Directly create a SUCCEEDED payment to simulate completed payment flow
    from app.models.payment import Payment, PaymentStatus, Transaction, TransactionType, TransactionStatus, LedgerEntry, EntryDirection, DesignerEarning, EarningStatus
    from app.core.config import settings

    payment = Payment(
        project_id=project_id,
        client_id=c_id,
        amount=10000,
        currency="INR",
        provider="test",
        status=PaymentStatus.SUCCEEDED,
    )
    db.add(payment)
    db.flush()

    commission = int(round(10000 * settings.PLATFORM_COMMISSION_RATE))
    net = 10000 - commission

    tx = Transaction(project_id=project_id, payment_id=payment.id,
                     type=TransactionType.PAYMENT, amount=10000,
                     currency="INR", status=TransactionStatus.COMPLETED)
    db.add(tx)
    db.flush()

    db.add(LedgerEntry(project_id=project_id, payment_id=payment.id,
                       transaction_id=tx.id, user_id=c_id,
                       entry_type="CLIENT_PAYMENT", amount=10000,
                       currency="INR", direction=EntryDirection.CREDIT,
                       description="Test payment"))

    earning = DesignerEarning(
        designer_id=dp_id, project_id=project_id, payment_id=payment.id,
        gross_amount=10000, platform_fee=commission, net_amount=net,
        currency="INR", status=EarningStatus.PENDING,
    )
    db.add(earning)
    db.commit()

    return project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id, payment.id


def test_full_refund_resolution(client: TestClient, db: Session):
    vals = _setup_project_with_payment(client, db, "fr1")
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id, payment_id = vals
    _, _, admin_hdrs = register_admin(client, db, "admin_fr1@test.com")

    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Design did not meet any of the agreed requirements.").json()["id"]
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "full_refund_to_client",
                          "resolution_note": "Delivery entirely failed to meet agreed requirements."},
                    headers=admin_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["resolution_type"] == "full_refund_to_client"

    # Verify payment status updated
    from app.models.payment import Payment, PaymentStatus, EarningStatus, DesignerEarning
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    assert payment.status == PaymentStatus.REFUNDED

    # Verify designer earning reversed
    earning = db.query(DesignerEarning).filter(DesignerEarning.payment_id == payment_id).first()
    assert earning.status == EarningStatus.REVERSED

    # Verify new ledger entries created (original preserved + refund entries added)
    entries = db.query(LedgerEntry).filter(LedgerEntry.payment_id == payment_id).all()
    entry_types = [e.entry_type for e in entries]
    assert "CLIENT_REFUND" in entry_types
    assert "CLIENT_PAYMENT" in entry_types  # original preserved


def test_partial_refund_resolution(client: TestClient, db: Session):
    vals = _setup_project_with_payment(client, db, "pr1")
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id, payment_id = vals
    _, _, admin_hdrs = register_admin(client, db, "admin_pr1@test.com")

    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Partial work was done but not to specification.").json()["id"]
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "partial_refund_to_client",
                          "resolution_note": "50% work was delivered; 50% refund issued.",
                          "resolution_amount": 5000},
                    headers=admin_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["resolution_amount"] == 5000

    from app.models.payment import Payment, PaymentStatus
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    assert payment.status == PaymentStatus.PARTIALLY_REFUNDED


def test_partial_refund_exceeds_payment_rejected(client: TestClient, db: Session):
    vals = _setup_project_with_payment(client, db, "pr2")
    project_id, c_id, c_tok, c_hdrs, *_ , payment_id = vals
    _, _, admin_hdrs = register_admin(client, db, "admin_pr2@test.com")

    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Requesting overpayment refund beyond total.").json()["id"]
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "partial_refund_to_client",
                          "resolution_note": "Trying to refund more than paid.",
                          "resolution_amount": 99999},
                    headers=admin_hdrs)
    assert r.status_code == 400, r.json()


def test_release_to_designer_resolution(client: TestClient, db: Session):
    vals = _setup_project_with_payment(client, db, "rd1")
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id, payment_id = vals
    _, _, admin_hdrs = register_admin(client, db, "admin_rd1@test.com")

    dispute_id = create_dispute(client, project_id, d_hdrs,
                                reason="non_responsive_party",
                                description="Client is refusing acceptance without valid reason repeatedly.").json()["id"]
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "release_to_designer",
                          "resolution_note": "Designer delivered quality work; client's refusal is unjustified."},
                    headers=admin_hdrs)
    assert r.status_code == 200, r.json()

    from app.models.payment import DesignerEarning, EarningStatus
    earning = db.query(DesignerEarning).filter(DesignerEarning.payment_id == payment_id).first()
    assert earning.status == EarningStatus.AVAILABLE


def test_ledger_history_preserved_after_refund(client: TestClient, db: Session):
    """Original financial entries must never be modified — only new entries appended."""
    vals = _setup_project_with_payment(client, db, "ledger1")
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id, payment_id = vals
    _, _, admin_hdrs = register_admin(client, db, "admin_ledger1@test.com")

    # Count original entries
    initial_count = db.query(LedgerEntry).filter(LedgerEntry.payment_id == payment_id).count()

    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Design is completely wrong and unusable.").json()["id"]
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)
    client.post(f"/disputes/{dispute_id}/resolve",
                json={"resolution_type": "full_refund_to_client",
                      "resolution_note": "Full refund issued; design failed all requirements."},
                headers=admin_hdrs)

    # Total entries should be MORE than before (new ones appended, originals intact)
    final_count = db.query(LedgerEntry).filter(LedgerEntry.payment_id == payment_id).count()
    assert final_count > initial_count


# ─────────────────────────────────────────────────────────────────────────────
# 8. Notifications and project events
# ─────────────────────────────────────────────────────────────────────────────

def test_dispute_created_notification_sent_to_opposing_party(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "notif1")
    create_dispute(client, project_id, c_hdrs,
                   description="I am disputing the quality of this delivery.")

    notifs = client.get("/notifications", headers=d_hdrs).json()
    types = [n["type"] for n in notifs["notifications"]]
    assert "dispute_created" in types


def test_dispute_creator_does_not_get_own_dispute_notification(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "notif2")
    create_dispute(client, project_id, c_hdrs,
                   description="Disputing the quality of the delivery work done.")

    c_notifs = client.get("/notifications", headers=c_hdrs).json()
    dispute_notifs = [n for n in c_notifs["notifications"] if n["type"] == "dispute_created"]
    assert len(dispute_notifs) == 0


def test_response_notification_sent_to_other_party(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "notif3")
    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="I am disputing this delivery quality.").json()["id"]
    client.post(f"/disputes/{dispute_id}/responses",
                json={"message": "Here is my detailed rebuttal to the raised dispute claim."},
                headers=d_hdrs)

    c_notifs = client.get("/notifications", headers=c_hdrs).json()
    types = [n["type"] for n in c_notifs["notifications"]]
    assert "dispute_response" in types


def test_resolution_notification_sent_to_both_parties(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "notif4")
    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Dispute about delivery quality.").json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_notif4@test.com")
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)
    client.post(f"/disputes/{dispute_id}/resolve",
                json={"resolution_type": "no_refund",
                      "resolution_note": "After review no valid grounds for refund were found."},
                headers=admin_hdrs)

    c_notifs = client.get("/notifications", headers=c_hdrs).json()
    d_notifs = client.get("/notifications", headers=d_hdrs).json()
    c_types = [n["type"] for n in c_notifs["notifications"]]
    d_types = [n["type"] for n in d_notifs["notifications"]]
    assert "dispute_resolved" in c_types
    assert "dispute_resolved" in d_types


# ─────────────────────────────────────────────────────────────────────────────
# 9. Admin reject
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_can_reject_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "rej1")
    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Disputing the overall project outcome.").json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_rej1@test.com")
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/reject",
                    json={"status": "rejected", "note": "No valid grounds; dispute is frivolous."},
                    headers=admin_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "rejected"


def test_non_admin_cannot_reject_dispute(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "rej2")
    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Disputing the quality of this design.").json()["id"]
    r = client.post(f"/disputes/{dispute_id}/reject",
                    json={"status": "rejected", "note": "No grounds."},
                    headers=c_hdrs)
    assert r.status_code == 403, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# 10. Mutual resolution
# ─────────────────────────────────────────────────────────────────────────────

def test_mutual_resolution(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "mut1")
    dispute_id = create_dispute(client, project_id, c_hdrs,
                                description="Both parties agree on a settlement.").json()["id"]
    _, _, admin_hdrs = register_admin(client, db, "admin_mut1@test.com")
    client.patch(f"/disputes/{dispute_id}/status", json={"status": "under_review"}, headers=admin_hdrs)

    r = client.post(f"/disputes/{dispute_id}/resolve",
                    json={"resolution_type": "mutual_resolution",
                          "resolution_note": "Both parties reached agreement outside the platform."},
                    headers=admin_hdrs)
    assert r.status_code == 200, r.json()
    assert r.json()["resolution_type"] == "mutual_resolution"


# ─────────────────────────────────────────────────────────────────────────────
# 11. Payment/project mismatch
# ─────────────────────────────────────────────────────────────────────────────

def test_payment_project_mismatch_rejected(client: TestClient, db: Session):
    project_id, c_id, c_tok, c_hdrs, d_id, d_tok, d_hdrs, dp_id = setup_project(client, db, "mismatch1")
    r = client.post(f"/projects/{project_id}/disputes",
                    json={"reason": "payment_issue",
                          "description": "Payment was made but not recorded properly here.",
                          "payment_id": 99999},
                    headers=c_hdrs)
    assert r.status_code == 400, r.json()
