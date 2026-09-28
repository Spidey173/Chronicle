"""API tests for Banking domain endpoints."""

import io
from fastapi import status


def test_upload_banking_csv(client, user_token_headers):
    csv_bytes = (
        b"transaction_ref,account_number,transaction_date,amount,transaction_type,category\n"
        b"TXN-TEST-1,ACC-CHK-1,2026-05-01,3000.0,Credit,Salary\n"
        b"TXN-TEST-2,ACC-CHK-1,2026-05-02,120.0,Debit,Groceries\n"
    )
    files = {"file": ("bank_txns.csv", io.BytesIO(csv_bytes), "text/csv")}
    data = {"domain": "banking"}

    response = client.post("/upload", files=files, data=data, headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "completed"
    assert response.json()["valid_records"] == 2


def test_get_transactions(client, user_token_headers):
    response = client.get("/transactions", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "pagination" in data


def test_get_accounts(client, user_token_headers):
    response = client.get("/accounts", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "pagination" in data
