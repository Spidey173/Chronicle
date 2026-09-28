"""API tests for Retail domain endpoints and file ingestion."""

import io
from fastapi import status


def test_upload_csv_pipeline(client, user_token_headers):
    csv_bytes = (
        b"order_number,customer_email,product_code,order_date,quantity,unit_price\n"
        b"ORD-API-01,client1@example.com,PRD-1,2026-05-15,1,150.0\n"
        b"ORD-API-02,client2@example.com,PRD-2,2026-05-16,2,75.0\n"
    )
    files = {"file": ("sales_feed.csv", io.BytesIO(csv_bytes), "text/csv")}
    data = {"domain": "retail"}

    response = client.post("/upload", files=files, data=data, headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    assert res["status"] == "completed"
    assert res["total_records"] == 2
    assert res["valid_records"] == 2
    assert res["rejected_records"] == 0


def test_get_orders(client, user_token_headers):
    response = client.get("/orders", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1


def test_get_customers(client, user_token_headers):
    response = client.get("/customers", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "pagination" in data


def test_get_products(client, user_token_headers):
    response = client.get("/products", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "pagination" in data


def test_get_batches_and_quarantine(client, user_token_headers):
    # Batches
    b_res = client.get("/api/v1/ingestion/batches", headers=user_token_headers)
    assert b_res.status_code == status.HTTP_200_OK
    assert "items" in b_res.json()

    # Quarantine
    q_res = client.get("/api/v1/ingestion/quarantine", headers=user_token_headers)
    assert q_res.status_code == status.HTTP_200_OK
    assert "items" in q_res.json()
