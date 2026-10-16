"""Cross-cutting behaviour: OpenAPI contract, error handlers, CORS, language middleware."""

from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.views import APIView

pytestmark = pytest.mark.django_db


def test_openapi_schema_is_valid_without_warnings(tmp_path) -> None:
    target = tmp_path / "openapi.yaml"
    call_command(
        "spectacular", "--file", str(target), "--validate", "--fail-on-warn", stdout=StringIO()
    )
    schema = target.read_text()
    for path in (
        "/api/v1/site/",
        "/api/v1/categories/",
        "/api/v1/services/",
        "/api/v1/bookings/",
        "/api/v1/bookings/slots/",
        "/api/v1/careers/applications/",
        "/api/v1/contact/",
        "/api/v1/gallery/",
    ):
        assert f"{path}:" in schema


def test_swagger_ui_is_served_without_cdn(client) -> None:
    response = client.get("/api/v1/docs/")
    assert response.status_code == 200
    assert b"cdn.jsdelivr" not in response.content


def test_unknown_api_route_returns_json_404(client) -> None:
    response = client.get("/api/v1/does-not-exist/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Ressource introuvable."}


def test_unknown_page_returns_branded_html_404(client) -> None:
    response = client.get("/nope/")
    assert response.status_code == 404
    assert b"Page introuvable" in response.content


def test_server_error_handlers(rf) -> None:
    from apps.core.exceptions import server_error

    api_response = server_error(rf.get("/api/v1/site/"))
    assert api_response.status_code == 500
    assert b"erreur interne" in api_response.content

    html_response = server_error(rf.get("/fr/"))
    assert html_response.status_code == 500
    assert b"Un petit souci technique" in html_response.content


def test_unexpected_exception_in_a_view_returns_json_500(rf, caplog) -> None:
    from apps.core.exceptions import api_exception_handler

    class Boom(APIView):
        pass

    response = api_exception_handler(RuntimeError("boom"), {"view": Boom()})
    assert response is not None
    assert response.status_code == 500
    assert "Unhandled API error in Boom" in caplog.text


def test_cors_allows_only_configured_origins(client, seeded, settings) -> None:
    allowed = client.get("/api/v1/site/", HTTP_ORIGIN="http://localhost:5173")
    assert allowed["Access-Control-Allow-Origin"] == "http://localhost:5173"

    denied = client.get("/api/v1/site/", HTTP_ORIGIN="https://evil.example")
    assert "Access-Control-Allow-Origin" not in denied


def test_content_language_header(client, seeded) -> None:
    assert client.get("/api/v1/site/?lang=en")["Content-Language"] == "en"
    assert client.get("/api/v1/site/")["Content-Language"] == "fr"


def test_security_headers(client, seeded) -> None:
    response = client.get("/api/v1/site/")
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
