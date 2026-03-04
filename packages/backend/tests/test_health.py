"""Tests for the health check endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    """GET /health should return 200."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_correct_body(client):
    """GET /health should return status ok and version."""
    response = await client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
