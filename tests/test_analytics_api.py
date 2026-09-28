"""API tests for Analytics and Health endpoints."""

from fastapi import status


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "timestamp" in data


def test_analytics_revenue(client, user_token_headers):
    response = client.get("/analytics/revenue", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_revenue" in data
    assert "average_order_value" in data
    assert "estimated_gross_profit" in data


def test_analytics_top_products(client, user_token_headers):
    response = client.get("/analytics/top-products", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_analytics_monthly_sales(client, user_token_headers):
    response = client.get("/analytics/monthly-sales", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_analytics_top_customers(client, user_token_headers):
    response = client.get("/analytics/top-customers", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_analytics_category_summary(client, user_token_headers):
    response = client.get("/analytics/category-summary", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_analytics_banking_summary(client, user_token_headers):
    response = client.get("/analytics/banking-summary", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_income_usd" in data
    assert "total_expenses_usd" in data
    assert "net_savings_usd" in data
    assert "spending_by_category" in data


def test_analytics_data_quality(client, user_token_headers):
    response = client.get("/analytics/data-quality", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "overall_quality_percentage" in data
    assert "total_records_processed" in data


def test_analytics_dashboard_summary(client):
    response = client.get("/api/v1/analytics/dashboard-summary")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "revenue" in data
    assert "data_quality" in data
    assert "banking" in data
    assert "monthly_sales" in data
    assert "categories" in data
