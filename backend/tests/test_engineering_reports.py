"""Tests for Engineering Intelligence Report Generator (CG-069)."""

import pytest
from fastapi.testclient import TestClient

from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager
from app.engineering_reports.exporters import (
    HtmlReportExporter,
    MarkdownReportExporter,
    get_exporter,
)
from app.engineering_reports.report_engine import report_engine
from app.main import app
from app.repository_memory.memory_engine import memory_engine
from app.schemas.engineering_reports import ReportFormat, ReportGenerateRequest, ReportType

client = TestClient(app)


def setup_function():
    cache_manager.invalidate("engineering_report:")
    cache_manager.invalidate("engineering_report_summary:")
    cache_manager.invalidate("timeline:")
    cache_manager.invalidate("impact_analysis:")
    cache_manager.invalidate("impact_summary:")


def test_exporters_json_and_markdown():
    report = report_engine.generate(
        "reports-export-1",
        ReportGenerateRequest(report_type=ReportType.EXECUTIVE, export_format=ReportFormat.JSON),
    )
    json_payload = get_exporter(ReportFormat.JSON).export(report)
    assert report.repository_id in json_payload
    md = MarkdownReportExporter().export(report)
    assert report.title in md
    assert "## Executive Summary" in md


def test_html_pdf_exporters_reserved():
    report = report_engine.generate("reports-stub-1", ReportGenerateRequest())
    with pytest.raises(NotImplementedError):
        HtmlReportExporter().export(report)
    with pytest.raises(NotImplementedError):
        get_exporter(ReportFormat.PDF).export(report)


def test_generate_executive_report_composes_sources():
    repo = "reports-exec-1"
    memory_engine.build_memory(repo)
    report = report_engine.generate(
        repo,
        ReportGenerateRequest(report_type=ReportType.EXECUTIVE),
    )
    assert report.repository_id == repo
    assert report.report_type == ReportType.EXECUTIVE
    assert report.executive_summary
    assert report.ai_engineering_summary
    assert report.repository_health_score.overall >= 0
    assert report.confidence_score > 0
    assert report.sections
    assert "Repository Memory" in report.sources_used or "Timeline Intelligence" in report.sources_used


def test_report_types():
    repo = "reports-types-1"
    for rtype in (
        ReportType.ARCHITECTURE,
        ReportType.TECHNICAL_DEBT,
        ReportType.REPOSITORY_HEALTH,
        ReportType.SECURITY_OVERVIEW,
        ReportType.IMPACT_ANALYSIS,
    ):
        report = report_engine.generate(repo, ReportGenerateRequest(report_type=rtype))
        assert report.report_type == rtype
        assert report.sections


def test_custom_report_sections():
    report = report_engine.generate(
        "reports-custom-1",
        ReportGenerateRequest(
            report_type=ReportType.CUSTOM,
            include_sections=["architecture", "impact", "recommendations"],
        ),
    )
    ids = [s.section_id for s in report.sections]
    assert ids == ["architecture", "impact", "recommendations"]


def test_markdown_export_via_request():
    report = report_engine.generate(
        "reports-md-1",
        ReportGenerateRequest(export_format=ReportFormat.MARKDOWN),
    )
    assert report.export_format == ReportFormat.MARKDOWN
    assert report.exported_content
    assert report.title in report.exported_content


def test_api_generate_list_summary():
    repo = "api-reports-1"
    gen = client.post(
        f"/reports/generate/{repo}",
        json={"report_type": "executive", "export_format": "json"},
    )
    assert gen.status_code == 200
    body = gen.json()
    assert body["repository_id"] == repo
    assert "executive_summary" in body
    assert "repository_health_score" in body
    assert "ai_engineering_summary" in body

    listed = client.get(f"/reports/{repo}")
    assert listed.status_code == 200
    assert listed.json()["count"] >= 1

    summary = client.get(f"/reports/{repo}/summary")
    assert summary.status_code == 200
    data = summary.json()
    assert data["repository_id"] == repo
    assert data["health_score"] >= 0
    assert data["summary"]


def test_api_summary_route_not_captured_as_repo_id():
    # Ensure /summary is registered and works
    repo = "api-reports-summary-route"
    assert client.post(f"/reports/generate/{repo}", json={}).status_code == 200
    assert client.get(f"/reports/{repo}/summary").status_code == 200


def test_regression_impact_and_timeline_still_work():
    assert client.get("/timeline/reports-regression-1").status_code == 200
    assert client.post(
        "/impact/analyze/reports-regression-2",
        json={"target": "services"},
    ).status_code == 200
    assert client.get("/health").status_code == 200


def test_cache_keys_reports():
    assert CacheKeys.engineering_report("r", "d") == "engineering_report:r:d"
    assert CacheKeys.engineering_report_summary("r") == "engineering_report_summary:r"
