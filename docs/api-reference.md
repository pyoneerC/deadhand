# API Reference

Deadhand provides a minimalist, secure API for programmatic heartbeat management and vault status queries.

## Authentication

All API requests require your **User ID** and **Heartbeat Token**, which are provided upon vault creation.

## Endpoints

### 1. Send Heartbeat (Reset Timer)

Restores the 90-day (or user-defined) countdown to zero.

**Endpoint:** `GET /heartbeat/{user_id}/{token}`

**Response:**
```json
{
  "status": "success",
  "message": "heartbeat received, timer reset",
  "next_check_in": "2026-05-04T12:00:00Z"
}
```

### 2. Vault Status

Check if a vault is active or if the trigger sequence has begun.

**Endpoint:** `GET /api/vault/status/{user_id}`

**Response:**
```json
{
  "vault_id": 42,
  "status": "active",
  "last_seen": "2026-02-01T10:00:00Z",
  "is_dead": false
}
```

---

## Webhooks

You can configure a custom webhook URL in your settings to receive notifications when:
-   A heartbeat is missed (Warning).
-   The vault is successfully triggered.
-   A recovery attempt is made.

---

## Rate Limiting

The API is limited to **60 requests per minute** per IP to prevent DDoS attacks against the heartbeat mechanism.
