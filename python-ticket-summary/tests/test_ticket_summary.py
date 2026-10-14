import json
import subprocess
import sys
from pathlib import Path

DEFAULT_CSV_HEADER = "ticket_id,created_at,resolved_at,category,priority,status\n"


CLI_PATH = str(Path(__file__).resolve().parent.parent / "ticket_summary.py")


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Helper to run ticket_summary.py as a CLI process."""
    cmd = [sys.executable, CLI_PATH, *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )


def test_missing_file_exits_with_error():
    result = run_cli("nonexistent_file.csv")
    assert result.returncode == 1
    assert "Error" in result.stderr or "not found" in result.stderr.lower()


def test_empty_file_exits_with_error(tmp_path: Path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    result = run_cli(str(empty_file))
    assert result.returncode == 1
    assert "Error" in result.stderr or "empty" in result.stderr.lower()


def test_category_counts_alphabetical(tmp_path: Path):
    csv_file = tmp_path / "tickets.csv"
    csv_content = DEFAULT_CSV_HEADER + (
        "T-1,2026-01-01 10:00:00,2026-01-01 11:00:00,Hardware,high,resolved\n"
        "T-2,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"
        "T-3,2026-01-01 10:00:00,2026-01-01 14:00:00,Billing,medium,resolved\n"
        "T-4,2026-01-01 10:00:00,2026-01-01 15:00:00,Access,high,resolved\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Access: 1" in result.stdout
    assert "Billing: 2" in result.stdout
    assert "Hardware: 1" in result.stdout

    access_idx = result.stdout.index("Access")
    billing_idx = result.stdout.index("Billing")
    hardware_idx = result.stdout.index("Hardware")
    assert access_idx < billing_idx < hardware_idx


def test_whitespace_trimming_in_headers_and_values(tmp_path: Path):
    csv_file = tmp_path / "whitespace.csv"
    csv_content = (
        " ticket_id , created_at , resolved_at , category , priority , status \n"
        " T-10 , 2026-01-01 10:00:00 , 2026-01-01 11:00:00 , Network , high , resolved \n"
        " T-11 , 2026-01-01 10:00:00 , 2026-01-01 12:00:00 , Network , low , resolved \n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Network: 2" in result.stdout


def test_overall_and_category_average_resolution_time(tmp_path: Path):
    csv_file = tmp_path / "resolution.csv"
    csv_content = (
        DEFAULT_CSV_HEADER
        + (
            "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"  # 2.0 hrs
            "T-2,2026-01-01 10:00:00,2026-01-01 16:00:00,Billing,medium,resolved\n"  # 6.0 hrs -> Billing avg: 4.0 hrs
            "T-3,2026-01-01 10:00:00,2026-01-02 10:00:00,Hardware,high,resolved\n"  # 24.0 hrs -> Hardware avg: 24.0 hrs
        )
    )
    # Total = 32.0 hrs / 3 = 10.67 hrs (0 days, 10 hours, 40 minutes)
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Average Resolution Time" in result.stdout
    assert "0 days, 10 hours, 40 minutes (10.67 hours)" in result.stdout
    # Category level resolution times
    assert (
        "Billing: 2 (Avg Resolution: 0 days, 4 hours, 0 minutes (4.00 hours))"
        in result.stdout
    )
    assert (
        "Hardware: 1 (Avg Resolution: 1 day, 0 hours, 0 minutes (24.00 hours))"
        in result.stdout
    )


def test_zero_resolved_tickets_displays_na(tmp_path: Path):
    csv_file = tmp_path / "unresolved.csv"
    csv_content = DEFAULT_CSV_HEADER + (
        "T-1,2026-01-01 10:00:00,,Support,low,open\n"
        "T-2,2026-01-01 10:00:00,,Support,high,in_progress\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Support: 2" in result.stdout
    assert "N/A (No resolved tickets)" in result.stdout


def test_iso_timestamp_variants_and_timezones(tmp_path: Path):
    csv_file = tmp_path / "iso_variants.csv"
    csv_content = (
        DEFAULT_CSV_HEADER
        + (
            "T-1,2026-01-01T10:00:00,2026-01-01T12:30:00,Ops,low,resolved\n"  # 2h 30m = 2.50h
            "T-2,2026-01-01T10:00:00Z,2026-01-01T14:00:00Z,Ops,high,resolved\n"  # 4h = 4.00h
        )
    )
    # Total = 6.5h / 2 = 3.25h -> 0 days, 3 hours, 15 minutes (3.25 hours)
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "0 days, 3 hours, 15 minutes (3.25 hours)" in result.stdout


def test_malformed_rows_logged_to_stderr_and_valid_processed(tmp_path: Path):
    csv_file = tmp_path / "malformed.csv"
    csv_content = (
        DEFAULT_CSV_HEADER
        + (
            ",2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"  # Row 2 missing ticket_id
            "T-99,bad-created-date,2026-01-01 11:00:00,Billing,low,resolved\n"  # T-99 bad created_at
            "T-98,2026-01-01 10:00:00,2026-01-01 11:00:00,,low,resolved\n"  # T-98 missing category
            "T-97,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,,resolved\n"  # T-97 missing priority
            "T-96,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,\n"  # T-96 missing status
            "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,high,resolved\n"  # valid
        )
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0

    assert "Row 2: Missing ticket_id" in result.stderr
    assert "T-99: Invalid or missing created_at" in result.stderr
    assert "T-98: Missing category" in result.stderr
    assert "T-97: Missing priority" in result.stderr
    assert "T-96: Missing status" in result.stderr

    assert "Billing: 1" in result.stdout


def test_skipped_tickets_reporting_on_stdout(tmp_path: Path):
    csv_file = tmp_path / "skipped.csv"
    csv_content = (
        DEFAULT_CSV_HEADER
        + (
            "T-100,2026-01-01 10:00:00,2026-01-01 12:00:00,DevOps,high,resolved\n"  # valid (2h)
            "T-101,2026-01-01 10:00:00,,DevOps,low,open\n"  # unresolved (missing date)
            "T-102,2026-01-02 10:00:00,2026-01-01 10:00:00,DevOps,medium,resolved\n"  # resolved before created
            "T-103,2026-01-01 10:00:00,corrupted-date,DevOps,low,resolved\n"  # invalid resolved_at
            "T-104,2026-01-01 10:00:00,2026-01-01 12:00:00,DevOps,low,in_progress\n"  # non-resolved status
        )
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0

    assert "T-102: Resolved date earlier than created date" in result.stderr
    assert "T-103: Invalid resolved_at timestamp" in result.stderr

    assert "Skipped Tickets (Resolution Time):" in result.stdout
    assert "Unresolved / Missing resolution date: T-101" in result.stdout
    assert "Unresolved / Non-resolved status: T-104" in result.stdout
    assert "Resolved before created: T-102" in result.stdout
    assert "Invalid resolution date: T-103" in result.stdout

    # Only T-100 (2 hours) counted in resolution
    assert "0 days, 2 hours, 0 minutes (2.00 hours)" in result.stdout
    # All 5 valid rows counted in DevOps
    assert "DevOps: 5" in result.stdout


def test_json_output_flag(tmp_path: Path):
    csv_file = tmp_path / "tickets.csv"
    csv_content = (
        DEFAULT_CSV_HEADER
        + (
            "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"  # 2.0 hrs
            "T-2,2026-01-01 10:00:00,2026-01-01 16:00:00,Billing,medium,resolved\n"  # 6.0 hrs
            "T-3,2026-01-01 10:00:00,,Hardware,high,open\n"  # unresolved
        )
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file), "--json")
    assert result.returncode == 0

    data = json.loads(result.stdout)
    assert data["category_counts"] == {"Billing": 2, "Hardware": 1}
    assert (
        data["overall_average_resolution_time"]
        == "0 days, 4 hours, 0 minutes (4.00 hours)"
    )
    assert (
        data["categories"]["Billing"]["average_resolution_time"]
        == "0 days, 4 hours, 0 minutes (4.00 hours)"
    )
    assert (
        data["categories"]["Hardware"]["average_resolution_time"]
        == "N/A (No resolved tickets)"
    )
    assert "T-3" in data["skipped_tickets"]["Unresolved / Missing resolution date"]


def test_json_output_with_warnings_keeps_stdout_valid_json(tmp_path: Path):
    csv_file = tmp_path / "mixed.csv"
    csv_content = (
        DEFAULT_CSV_HEADER
        + (
            ",2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"  # Row 2 missing ticket_id
            "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,high,resolved\n"  # valid
        )
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file), "--json")
    assert result.returncode == 0

    assert "Row 2: Missing ticket_id" in result.stderr
    data = json.loads(result.stdout)
    assert data["category_counts"] == {"Billing": 1}


def test_category_casing_merged_to_canonical(tmp_path: Path):
    csv_file = tmp_path / "casing.csv"
    csv_content = DEFAULT_CSV_HEADER + (
        "T-1,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"
        "T-2,2026-01-01 10:00:00,2026-01-01 12:00:00,billing,normal,resolved\n"
        "T-3,2026-01-01 10:00:00,2026-01-01 13:00:00,BILLING,high,resolved\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Billing: 3" in result.stdout
    assert "billing: 1" not in result.stdout
    assert "BILLING: 1" not in result.stdout


def test_escalated_tickets_section(tmp_path: Path):
    csv_file = tmp_path / "escalated.csv"
    csv_content = DEFAULT_CSV_HEADER + (
        "T-1,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"
        "T-2,2026-01-01 10:00:00,,Billing,normal,escalated\n"
        "T-3,2026-01-01 10:00:00,,Billing,normal,escalatd\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Escalated Tickets:" in result.stdout
    assert "T-2" in result.stdout
    assert "T-3" in result.stdout

    json_result = run_cli(str(csv_file), "--json")
    data = json.loads(json_result.stdout)
    assert "escalated_tickets" in data
    assert "T-2" in data["escalated_tickets"]
    assert "T-3" in data["escalated_tickets"]


def test_extra_column_note_handling(tmp_path: Path):
    csv_file = tmp_path / "extra_col.csv"
    csv_content = DEFAULT_CSV_HEADER + (
        "TCK-2999,2026-03-09 10:13,,Refunds,normal,open,note: sent by phone\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Ticket Notes:" in result.stdout
    assert "TCK-2999: note: sent by phone" in result.stdout

    json_result = run_cli(str(csv_file), "--json")
    data = json.loads(json_result.stdout)
    assert "ticket_notes" in data
    assert data["ticket_notes"].get("TCK-2999") == "note: sent by phone"


def test_resolved_tickets_section(tmp_path: Path):
    csv_file = tmp_path / "resolved.csv"
    csv_content = DEFAULT_CSV_HEADER + (
        "T-10,2026-01-01 10:00:00,2026-01-01 11:00:00,Hardware,high,resolved\n"
        "T-20,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,closed\n"
        "T-30,2026-01-01 10:00:00,,Billing,medium,open\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Resolved Tickets:" in result.stdout
    assert "T-10" in result.stdout
    assert "T-20" in result.stdout
    assert (
        "T-30"
        not in result.stdout.split("Resolved Tickets:")[1].split("Skipped Tickets")[0]
    )

    json_result = run_cli(str(csv_file), "--json")
    data = json.loads(json_result.stdout)
    assert "resolved_tickets" in data
    assert data["resolved_tickets"] == ["T-10", "T-20"]
