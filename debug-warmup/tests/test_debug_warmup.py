"""Tests for SLA breach reporting module."""
import pytest
from debug_warmup import breach_report


@pytest.fixture
def default_sla():
    """Default SLA thresholds mapping priority names to hours."""
    return {"urgent": 4, "high": 8, "normal": 24, "low": 72}


def test_docstring_sample_breach_report(default_sla):
    """Verify SLA breach report matching the docstring specification."""
    sample = [
        {
            "ticket_id": "A",
            "priority": "urgent",
            "created_at": "2026-03-02 09:00",
            "resolved_at": "2026-03-02 12:00",
        },
        {
            "ticket_id": "B",
            "priority": "normal",
            "created_at": "2026-03-02 09:00",
            "resolved_at": "2026-03-03 11:00",
        },
        {
            "ticket_id": "C",
            "priority": "high",
            "created_at": "2026-03-02 09:00",
            "resolved_at": "2026-03-02 19:00",
        },
        {
            "ticket_id": "D",
            "priority": "low",
            "created_at": "2026-03-02 09:00",
            "resolved_at": "",
        },
    ]
    result = breach_report(sample, default_sla)
    assert result == {"breached": ["B", "C"], "average_hours": 13.0, "counted": 3}


def test_same_day_resolution(default_sla):
    """Verify calculations for tickets resolved on the same calendar day."""
    tickets = [
        {
            "ticket_id": "T1",
            "priority": "urgent",
            "created_at": "2026-03-01 08:00",
            "resolved_at": "2026-03-01 10:30",
        },
        {
            "ticket_id": "T2",
            "priority": "normal",
            "created_at": "2026-03-01 08:00",
            "resolved_at": "2026-03-01 13:00",
        },
    ]
    # T1: 2.5 hours (urgent SLA 4 -> ok)
    # T2: 5.0 hours (normal SLA 24 -> ok)
    result = breach_report(tickets, default_sla)
    assert result == {"breached": [], "average_hours": 3.75, "counted": 2}


def test_multi_day_over_24_hours(default_sla):
    """Verify duration calculation spanning across days exceeding 24 hours."""
    tickets = [
        {
            "ticket_id": "M24",
            "priority": "normal",
            "created_at": "2026-03-01 09:00",
            "resolved_at": "2026-03-02 13:00",
        }
    ]
    # 1 day and 4 hours = 28.0 hours (exceeds normal SLA 24 -> breached)
    result = breach_report(tickets, default_sla)
    assert result == {"breached": ["M24"], "average_hours": 28.0, "counted": 1}


def test_multi_day_over_48_hours():
    """Verify duration calculation spanning multiple days exceeding 48 hours."""
    sla = {"low": 48}
    tickets = [
        {
            "ticket_id": "M1",
            "priority": "low",
            "created_at": "2026-03-01 10:00",
            "resolved_at": "2026-03-03 12:00",
        }
    ]
    # 2 days and 2 hours = 50.0 hours (exceeds SLA 48 -> breached)
    result = breach_report(tickets, sla)
    assert result == {"breached": ["M1"], "average_hours": 50.0, "counted": 1}


def test_unresolved_and_empty_tickets(default_sla):
    """Verify behavior with empty ticket list and uncompleted tickets."""
    assert breach_report([], default_sla) == {
        "breached": [],
        "average_hours": 0.0,
        "counted": 0,
    }
    unresolved_only = [
        {
            "ticket_id": "U1",
            "priority": "normal",
            "created_at": "2026-03-01 10:00",
            "resolved_at": "",
        },
        {"ticket_id": "U2", "priority": "normal", "created_at": "2026-03-01 10:00"},
    ]
    assert breach_report(unresolved_only, default_sla) == {
        "breached": [],
        "average_hours": 0.0,
        "counted": 0,
    }


def test_exact_sla_boundary_not_breached(default_sla):
    """Verify that resolving exactly at the SLA limit is not considered breached."""
    tickets = [
        {
            "ticket_id": "E1",
            "priority": "high",
            "created_at": "2026-03-01 09:00",
            "resolved_at": "2026-03-01 17:00",
        }
    ]
    result = breach_report(tickets, default_sla)
    assert result == {"breached": [], "average_hours": 8.0, "counted": 1}
