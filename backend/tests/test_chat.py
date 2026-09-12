"""
tests/test_chat.py — Project Chat & Messaging tests.

Covers:
  - Conversation creation and duplicate prevention
  - Authorization (client, assigned designer, unrelated user)
  - Send, list, get single message
  - Soft-delete (sender only, content redacted)
  - Edit message (sender only)
  - Reply validation (same conversation, not deleted)
  - Read receipts and unread count
  - Notification integration (recipient gets NEW_MESSAGE, sender does not)
  - Notification preference respected
  - WebSocket: auth, connect, send, broadcast
  - Empty / oversized message rejected
"""
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def register_and_login(client, email, password="password123", full_name="Test User", role="CLIENT"):
    """Register a user and return (user_id, token, auth_headers)."""
    r = client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": full_name, "role": role},
    )
    assert r.status_code == 201, f"register failed: {r.json()}"
    user_id = r.json()["id"]
    tok = client.post("/auth/login", json={"email": email, "password": password})
    assert tok.status_code == 200, f"login failed: {tok.json()}"
    token = tok.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, token, headers


def create_project(client, headers, title="Chat Test Project"):
    r = client.post("/projects/", json={"title": title, "description": "desc"}, headers=headers)
    assert r.status_code == 201, f"create_project failed: {r.json()}"
    return r.json()["id"]


def create_designer_profile(client, headers):
    r = client.post("/profiles/designer", json={"bio": "bio", "hourly_rate": 5000}, headers=headers)
    assert r.status_code in (200, 201), f"create designer profile failed: {r.json()}"
    return r.json()["id"]


def setup_project_with_designer(client, db, suffix=""):
    """Create client, designer, project, send and accept invitation.
    Returns (project_id, client_headers, designer_headers, client_token, designer_token).
    """
    c_id, c_tok, c_hdrs = register_and_login(
        client, f"chatclient{suffix}@test.com", role="CLIENT"
    )
    d_id, d_tok, d_hdrs = register_and_login(
        client, f"chatdesigner{suffix}@test.com", role="DESIGNER"
    )
    designer_profile_id = create_designer_profile(client, d_hdrs)
    project_id = create_project(client, c_hdrs, title=f"Project {suffix}")

    # Client invites designer
    inv = client.post(
        f"/projects/{project_id}/invite",
        json={"designer_id": designer_profile_id},
        headers=c_hdrs,
    )
    assert inv.status_code == 201, f"invite failed: {inv.json()}"
    inv_id = inv.json()["id"]

    # Designer accepts
    acc = client.post(f"/invitations/{inv_id}/accept", headers=d_hdrs)
    assert acc.status_code == 200, f"accept failed: {acc.json()}"

    return project_id, c_hdrs, d_hdrs, c_tok, d_tok


# ─────────────────────────────────────────────────────────────────────────────
# Conversation tests
# ─────────────────────────────────────────────────────────────────────────────

def test_conversation_created_for_valid_project(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "cv1")
    r = client.get(f"/projects/{project_id}/chat", headers=c_hdrs)
    assert r.status_code == 200, r.json()
    data = r.json()
    assert data["project_id"] == project_id
    assert "id" in data


def test_conversation_no_duplicate(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "cv2")
    r1 = client.get(f"/projects/{project_id}/chat", headers=c_hdrs)
    r2 = client.get(f"/projects/{project_id}/chat", headers=c_hdrs)
    assert r1.json()["id"] == r2.json()["id"]


def test_designer_can_access_conversation(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "cv3")
    r = client.get(f"/projects/{project_id}/chat", headers=d_hdrs)
    assert r.status_code == 200, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# Authorization tests
# ─────────────────────────────────────────────────────────────────────────────

def test_unrelated_client_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "auth1")
    _, _, other_hdrs = register_and_login(client, "other_client_auth1@test.com", role="CLIENT")
    r = client.get(f"/projects/{project_id}/chat", headers=other_hdrs)
    assert r.status_code == 403, r.json()


def test_unrelated_designer_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "auth2")
    _, _, other_hdrs = register_and_login(client, "other_designer_auth2@test.com", role="DESIGNER")
    r = client.get(f"/projects/{project_id}/chat", headers=other_hdrs)
    assert r.status_code == 403, r.json()


def test_unauthenticated_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "auth3")
    r = client.get(f"/projects/{project_id}/chat")
    assert r.status_code == 401, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# Message send / list tests
# ─────────────────────────────────────────────────────────────────────────────

def test_send_and_list_messages(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "msg1")

    r = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Hello designer!", "message_type": "text"},
        headers=c_hdrs,
    )
    assert r.status_code == 201, r.json()
    msg = r.json()
    assert msg["content"] == "Hello designer!"
    assert msg["is_deleted"] is False

    r2 = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Hi client!", "message_type": "text"},
        headers=d_hdrs,
    )
    assert r2.status_code == 201, r2.json()

    r3 = client.get(f"/projects/{project_id}/chat/messages", headers=c_hdrs)
    assert r3.status_code == 200, r3.json()
    data = r3.json()
    assert data["total"] == 2
    assert len(data["messages"]) == 2


def test_empty_message_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, *_ = setup_project_with_designer(client, db, "msg2")
    # Pydantic min_length=1 will catch this with 422
    r = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "", "message_type": "text"},
        headers=c_hdrs,
    )
    assert r.status_code == 422, r.json()


def test_oversized_message_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, *_ = setup_project_with_designer(client, db, "msg3")
    r = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "x" * 4001, "message_type": "text"},
        headers=c_hdrs,
    )
    assert r.status_code == 422, r.json()


def test_correct_sender(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "msg4")
    c_me = client.get("/users/me", headers=c_hdrs).json()
    c_user_id = c_me["id"]

    r = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Who am I?", "message_type": "text"},
        headers=c_hdrs,
    )
    assert r.json()["sender_id"] == c_user_id


# ─────────────────────────────────────────────────────────────────────────────
# Reply tests
# ─────────────────────────────────────────────────────────────────────────────

def test_valid_reply(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "rep1")

    orig = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Original", "message_type": "text"},
        headers=c_hdrs,
    )
    orig_id = orig.json()["id"]

    reply = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Reply", "message_type": "text", "reply_to_message_id": orig_id},
        headers=d_hdrs,
    )
    assert reply.status_code == 201, reply.json()
    assert reply.json()["reply_to_message_id"] == orig_id


def test_nonexistent_reply_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, *_ = setup_project_with_designer(client, db, "rep2")
    r = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Reply to ghost", "message_type": "text", "reply_to_message_id": 99999},
        headers=c_hdrs,
    )
    assert r.status_code == 400, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# Soft-delete tests
# ─────────────────────────────────────────────────────────────────────────────

def test_sender_can_delete_own_message(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "del1")

    msg = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Delete me", "message_type": "text"},
        headers=c_hdrs,
    )
    msg_id = msg.json()["id"]

    del_r = client.delete(f"/projects/{project_id}/chat/messages/{msg_id}", headers=c_hdrs)
    assert del_r.status_code == 200, del_r.json()
    assert del_r.json()["is_deleted"] is True
    assert del_r.json()["content"] == "This message was deleted."


def test_other_user_cannot_delete_message(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "del2")

    msg = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "My message", "message_type": "text"},
        headers=c_hdrs,
    )
    msg_id = msg.json()["id"]

    del_r = client.delete(f"/projects/{project_id}/chat/messages/{msg_id}", headers=d_hdrs)
    assert del_r.status_code == 403, del_r.json()


def test_deleted_message_content_redacted_in_list(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "del3")

    msg = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Secret", "message_type": "text"},
        headers=c_hdrs,
    )
    msg_id = msg.json()["id"]
    client.delete(f"/projects/{project_id}/chat/messages/{msg_id}", headers=c_hdrs)

    msgs = client.get(f"/projects/{project_id}/chat/messages", headers=d_hdrs).json()["messages"]
    deleted = next(m for m in msgs if m["id"] == msg_id)
    assert deleted["content"] == "This message was deleted."
    assert deleted["is_deleted"] is True


def test_reply_to_deleted_message_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "del4")

    msg = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Will be deleted", "message_type": "text"},
        headers=c_hdrs,
    )
    msg_id = msg.json()["id"]
    client.delete(f"/projects/{project_id}/chat/messages/{msg_id}", headers=c_hdrs)

    r = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Reply to deleted", "message_type": "text", "reply_to_message_id": msg_id},
        headers=d_hdrs,
    )
    assert r.status_code == 400, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# Edit tests
# ─────────────────────────────────────────────────────────────────────────────

def test_sender_can_edit_own_message(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "edit1")

    msg = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Original content", "message_type": "text"},
        headers=c_hdrs,
    )
    msg_id = msg.json()["id"]

    edited = client.patch(
        f"/projects/{project_id}/chat/messages/{msg_id}",
        json={"content": "Edited content"},
        headers=c_hdrs,
    )
    assert edited.status_code == 200, edited.json()
    assert edited.json()["content"] == "Edited content"


def test_other_user_cannot_edit_message(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "edit2")

    msg = client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Client message", "message_type": "text"},
        headers=c_hdrs,
    )
    msg_id = msg.json()["id"]

    r = client.patch(
        f"/projects/{project_id}/chat/messages/{msg_id}",
        json={"content": "Hacked"},
        headers=d_hdrs,
    )
    assert r.status_code == 403, r.json()


# ─────────────────────────────────────────────────────────────────────────────
# Read state tests
# ─────────────────────────────────────────────────────────────────────────────

def test_unread_count_and_mark_read(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "read1")

    # Client sends 3 messages
    for i in range(3):
        client.post(
            f"/projects/{project_id}/chat/messages",
            json={"content": f"Message {i}", "message_type": "text"},
            headers=c_hdrs,
        )

    # Designer checks unread count
    count_r = client.get(f"/projects/{project_id}/chat/unread-count", headers=d_hdrs)
    assert count_r.status_code == 200, count_r.json()
    assert count_r.json()["unread_count"] == 3

    # Designer marks as read
    read_r = client.patch(f"/projects/{project_id}/chat/read", headers=d_hdrs)
    assert read_r.status_code == 200, read_r.json()
    assert read_r.json()["updated"] is True

    # Unread count should now be 0
    count_r2 = client.get(f"/projects/{project_id}/chat/unread-count", headers=d_hdrs)
    assert count_r2.json()["unread_count"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Notification integration tests
# ─────────────────────────────────────────────────────────────────────────────

def test_recipient_gets_new_message_notification(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "notif1")

    client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Hey!", "message_type": "text"},
        headers=c_hdrs,
    )

    # Designer's notifications should contain a NEW_MESSAGE notification
    notifs = client.get("/notifications", headers=d_hdrs).json()
    types = [n["type"] for n in notifs["notifications"]]
    assert "new_message" in types, f"Expected new_message in {types}"


def test_sender_does_not_get_own_message_notification(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "notif2")

    client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "Hey!", "message_type": "text"},
        headers=c_hdrs,
    )

    # Client (sender) should NOT get a new_message notification for their own message
    c_notifs = client.get("/notifications", headers=c_hdrs).json()
    own_msg_notifs = [n for n in c_notifs["notifications"] if n["type"] == "new_message"]
    assert len(own_msg_notifs) == 0


def test_notification_preference_respected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "notif3")

    # Disable new_message notifications for designer
    client.patch(
        "/notifications/preferences/new_message",
        headers=d_hdrs,
        json={"in_app_enabled": False},
    )

    client.post(
        f"/projects/{project_id}/chat/messages",
        json={"content": "You won't see a notification", "message_type": "text"},
        headers=c_hdrs,
    )

    # Designer should have no NEW_MESSAGE notifications
    notifs = client.get("/notifications", headers=d_hdrs).json()
    new_msg_notifs = [n for n in notifs["notifications"] if n["type"] == "new_message"]
    assert len(new_msg_notifs) == 0


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket tests
# ─────────────────────────────────────────────────────────────────────────────

def test_websocket_unauthenticated_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "ws1")
    rejected = False
    try:
        with client.websocket_connect(f"/ws/projects/{project_id}/chat") as ws:
            ws.receive_text()
    except Exception:
        rejected = True
    # Either the connection raises or the server closes it — both indicate rejection
    assert rejected


def test_websocket_authenticated_send_and_receive(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, c_tok, d_tok = setup_project_with_designer(client, db, "ws2")

    with client.websocket_connect(f"/ws/projects/{project_id}/chat?token={c_tok}") as ws:
        ws.send_text(json.dumps({"content": "WS Hello!", "message_type": "text"}))
        resp = ws.receive_text()
        data = json.loads(resp)
        assert data["type"] == "message.created"
        assert data["message"]["content"] == "WS Hello!"

    # Verify message was persisted via REST
    msgs = client.get(f"/projects/{project_id}/chat/messages", headers=c_hdrs)
    contents = [m["content"] for m in msgs.json()["messages"]]
    assert "WS Hello!" in contents


def test_websocket_unauthorized_user_rejected(client: TestClient, db: Session):
    project_id, c_hdrs, d_hdrs, *_ = setup_project_with_designer(client, db, "ws3")
    _, other_tok, _ = register_and_login(client, "ws_other_ws3@test.com", role="CLIENT")

    rejected = False
    try:
        with client.websocket_connect(f"/ws/projects/{project_id}/chat?token={other_tok}") as ws:
            ws.receive_text()
    except Exception:
        rejected = True
    assert rejected
