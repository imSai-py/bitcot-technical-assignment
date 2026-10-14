import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ticket_summary import compute_metrics, read_and_validate_csv

DEFAULT_CSV_HEADER = "ticket_id,created_at,resolved_at,category,priority,status\n"


def test_compute_metrics_does_not_mutate_input_rows():
    """Standards Review finding 1: isolated state."""
    original_rows = [
        {
            "ticket_id": "T-1",
            "created_at": "2026-01-01 10:00:00",
            "resolved_at": "2026-01-01 11:00:00",
            "category": "billing",
            "priority": "low",
            "status": "resolved",
        }
    ]
    rows_copy = copy.deepcopy(original_rows)
    metrics, _ = compute_metrics(original_rows)

    # original_rows should NOT be mutated in place
    assert original_rows == rows_copy
    assert original_rows[0]["category"] == "billing"
    assert metrics.category_counts["Billing"] == 1


def test_resolved_tickets_includes_tickets_with_missing_timestamps():
    """Spec Review finding 1: resolved tickets decoupled from duration math."""
    rows = [
        # T-1: resolved with duration
        {
            "ticket_id": "T-1",
            "created_at": "2026-01-01 10:00:00",
            "resolved_at": "2026-01-01 11:00:00",
            "category": "Billing",
            "priority": "low",
            "status": "resolved",
        },
        # T-2: resolved status but missing resolved_at (e.g. TCK-1139)
        {
            "ticket_id": "T-2",
            "created_at": "2026-01-01 10:00:00",
            "resolved_at": "",
            "category": "Billing",
            "priority": "low",
            "status": "resolved",
        },
        # T-3: open status
        {
            "ticket_id": "T-3",
            "created_at": "2026-01-01 10:00:00",
            "resolved_at": "",
            "category": "Billing",
            "priority": "low",
            "status": "open",
        },
    ]

    metrics, _ = compute_metrics(rows)
    # T-1 and T-2 have resolved status
    assert "T-1" in metrics.resolved_tickets
    assert "T-2" in metrics.resolved_tickets
    assert "T-3" not in metrics.resolved_tickets
    # Only T-1 had valid duration; T-2 is tracked in skipped_tickets for duration
    assert "T-2" in metrics.skipped_tickets["Unresolved / Missing resolution date"]


def test_note_from_header_column(tmp_path: Path):
    """Spec Review finding 2: notes defined in CSV header column."""
    csv_file = tmp_path / "note_header.csv"
    csv_content = (
        "ticket_id,created_at,resolved_at,category,priority,status,notes\n"
        "T-10,2026-01-01 10:00,2026-01-01 11:00,Billing,low,resolved,urgent note\n"
    )

    csv_file.write_text(csv_content, encoding="utf-8")

    rows, _, _ = read_and_validate_csv(csv_file)
    metrics, _ = compute_metrics(rows)
    assert metrics.ticket_notes.get("T-10") == "urgent note"


def test_duplicate_ticket_ids_skipped_and_warned(tmp_path: Path):
    """Lead feedback 1: duplicate ticket IDs skipped."""
    csv_file = tmp_path / "duplicates.csv"
    csv_content = (
        "ticket_id,created_at,resolved_at,category,priority,status\n"
        "T-101,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"
        "T-101,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,high,resolved\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    rows, fatal, warnings = read_and_validate_csv(csv_file)
    assert len(rows) == 1
    assert any("Duplicate ticket ID" in w for w in warnings)


def test_invalid_ticket_id_placeholder_rejected(tmp_path: Path):
    """Lead feedback 3: invalid placeholder N/A ticket ID rejected."""
    csv_file = tmp_path / "invalid_id.csv"
    csv_content = (
        "ticket_id,created_at,resolved_at,category,priority,status\n"
        "N/A,2026-01-01 10:00:00,2026-01-01 11:00:00,Account,urgent,resolved\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    rows, fatal, warnings = read_and_validate_csv(csv_file)
    assert len(rows) == 0
    assert any("Invalid ticket_id 'N/A'" in w for w in warnings)
