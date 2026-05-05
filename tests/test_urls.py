from __future__ import annotations


def test_root_redirects_to_admin(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response["Location"] == "/admin/"
