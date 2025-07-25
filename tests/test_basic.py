# tests/test_basic.py

import pytest
from app.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    resp = client.get('/')
    assert resp.status_code == 200

def test_shorten_and_redirect(client):
    url = "https://example.com"
    resp = client.post('/api/shorten', json={"url": url})
    assert resp.status_code == 201
    data = resp.get_json()
    short_code = data["short_code"]
    redirect_resp = client.get(f'/{short_code}', follow_redirects=False)
    assert redirect_resp.status_code == 302

def test_shorten_invalid_url(client):
    resp = client.post('/api/shorten', json={"url": "invalid"})
    assert resp.status_code == 400

def test_redirect_not_found(client):
    resp = client.get('/notarealcode')
    assert resp.status_code == 404

def test_stats(client):
    url = "https://stats.com"
    resp = client.post('/api/shorten', json={"url": url})
    short_code = resp.get_json()["short_code"]
    # One redirect
    client.get(f'/{short_code}')
    stats = client.get(f'/api/stats/{short_code}')
    data = stats.get_json()
    assert data["url"] == url
    assert data["clicks"] == 1
    assert "created_at" in data
