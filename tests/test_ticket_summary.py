import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Helper to run ticket_summary.py as a CLI process."""
    cmd = [sys.executable, "ticket_summary.py", *args]
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
    csv_content = (
        "ticket_id,created_at,resolved_at,category,priority,status\n"
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

    # Verify alphabetical order in stdout
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
        "ticket_id,created_at,resolved_at,category,priority,status\n"
        "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"  # 2.0 hrs
        "T-2,2026-01-01 10:00:00,2026-01-01 16:00:00,Billing,medium,resolved\n"  # 6.0 hrs -> Billing avg: 4.0 hrs
        "T-3,2026-01-01 10:00:00,2026-01-02 10:00:00,Hardware,high,resolved\n"  # 24.0 hrs -> Hardware avg: 24.0 hrs
    )
    # Total = 32.0 hrs / 3 = 10.67 hrs (10 hours, 40 minutes)
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "Average Resolution Time" in result.stdout
    assert "10 hours, 40 minutes (10.67 hours)" in result.stdout
    # Category level resolution times
    assert (
        "Billing: 2 (Avg Resolution: 4 hours, 0 minutes (4.00 hours))" in result.stdout
    )
    assert (
        "Hardware: 1 (Avg Resolution: 1 day, 0 hours, 0 minutes (24.00 hours))"
        in result.stdout
    )


def test_zero_resolved_tickets_displays_na(tmp_path: Path):
    csv_file = tmp_path / "unresolved.csv"
    csv_content = (
        "ticket_id,created_at,resolved_at,category,priority,status\n"
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
        "ticket_id,created_at,resolved_at,category,priority,status\n"
        "T-1,2026-01-01T10:00:00,2026-01-01T12:30:00,Ops,low,resolved\n"  # 2h 30m = 2.50h
        "T-2,2026-01-01T10:00:00Z,2026-01-01T14:00:00Z,Ops,high,resolved\n"  # 4h = 4.00h
    )
    # Total = 6.5h / 2 = 3.25h -> 3 hours, 15 minutes (3.25 hours)
    csv_file.write_text(csv_content, encoding="utf-8")

    result = run_cli(str(csv_file))
    assert result.returncode == 0
    assert "3 hours, 15 minutes (3.25 hours)" in result.stdout
