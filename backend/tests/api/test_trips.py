import pytest


@pytest.mark.asyncio
async def test_list_trips_empty(client):
    response = await client.get("/api/v1/trips")
    assert response.status_code == 200
    body = response.json()
    assert body["data"] == []
    assert body["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_get_trip_not_found(client):
    response = await client.get("/api/v1/trips/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
