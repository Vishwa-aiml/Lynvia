import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.notification import NotificationType, Notification
from app.models.notification_preference import NotificationPreference


def test_notification_creation_and_preferences(client: TestClient, db: Session):
    # Register and login user
    res_reg = client.post("/auth/register", json={"email": "notify@example.com", "password": "password123", "full_name": "Notify"})
    assert res_reg.status_code == 201
    user_id = res_reg.json()["id"]

    res_login = client.post("/auth/login", json={"email": "notify@example.com", "password": "password123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check preferences default to true for in-app
    pref_res = client.get("/notifications/preferences", headers=headers)
    assert pref_res.status_code == 200
    assert len(pref_res.json()) == 0  # No preferences explicitly set yet

    # 2. Fire an event that creates a notification
    import app.services.notifications as notif_svc
    notif = notif_svc.create_notification(
        db=db,
        recipient_id=user_id,
        notification_type=NotificationType.SYSTEM,
        title="Test Notification",
        message="This is a test message",
        entity_type="system",
        entity_id=1,
    )
    db.commit()
    assert notif is not None
    assert notif.is_read is False

    # 3. Fetch notifications
    res = client.get("/notifications", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["unread_count"] == 1
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Test Notification"

    # 4. Fetch unread count
    res_count = client.get("/notifications/unread-count", headers=headers)
    assert res_count.status_code == 200
    assert res_count.json()["count"] == 1

    # 5. Mark as read
    notif_id = data["notifications"][0]["id"]
    res_read = client.patch(f"/notifications/{notif_id}/read", headers=headers)
    assert res_read.status_code == 200

    # 6. Verify unread count is 0
    res_count2 = client.get("/notifications/unread-count", headers=headers)
    assert res_count2.json()["count"] == 0

    # 7. Update preference to disable system notifications
    res_pref = client.patch(
        "/notifications/preferences/system",
        headers=headers,
        json={"in_app_enabled": False}
    )
    assert res_pref.status_code == 200
    assert res_pref.json()["in_app_enabled"] is False

    # 8. Try creating another system notification
    notif2 = notif_svc.create_notification(
        db=db,
        recipient_id=user_id,
        notification_type=NotificationType.SYSTEM,
        title="Test Notification 2",
        message="This should be suppressed",
    )
    db.commit()
    assert notif2 is None  # Suppressed by preference

    # 9. Verify total is still 1
    res_final = client.get("/notifications", headers=headers)
    assert res_final.json()["total"] == 1


def test_mark_all_as_read(client: TestClient, db: Session):
    res_reg = client.post("/auth/register", json={"email": "notify2@example.com", "password": "password123", "full_name": "Notify 2"})
    user_id = res_reg.json()["id"]

    res_login = client.post("/auth/login", json={"email": "notify2@example.com", "password": "password123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    import app.services.notifications as notif_svc
    
    # Enable system notifications again
    notif_svc.update_preference(db, user_id, NotificationType.SYSTEM, in_app_enabled=True)

    notif_svc.create_bulk_notifications(
        db=db,
        recipient_ids=[user_id],
        notification_type=NotificationType.SYSTEM,
        title="Bulk 1",
        message="Message 1"
    )
    notif_svc.create_bulk_notifications(
        db=db,
        recipient_ids=[user_id],
        notification_type=NotificationType.SYSTEM,
        title="Bulk 2",
        message="Message 2"
    )
    db.commit()

    count_res = client.get("/notifications/unread-count", headers=headers)
    assert count_res.json()["count"] >= 2

    # Mark all read
    read_all_res = client.patch("/notifications/read-all", headers=headers)
    assert read_all_res.status_code == 200

    count_res_after = client.get("/notifications/unread-count", headers=headers)
    assert count_res_after.json()["count"] == 0
