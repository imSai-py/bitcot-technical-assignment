"""Verification test harness for Python Ticket Summary CLI tool.

Exercises the real CLI tool, verifies expected output and error behavior,
and writes persistent evidence artifacts to an evidence directory.
Standard library only.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_DIR = REPO_ROOT / "python-ticket-summary"
ENTRY_POINT = APP_DIR / "ticket_summary.py"
DEFAULT_CSV = APP_DIR / "tickets.csv"
DEFAULT_EVIDENCE_DIR = REPO_ROOT / "artifacts" / "verify-ticket-summary"

CSV_HEADER = "ticket_id,created_at,resolved_at,category,priority,status\n"


def run_command(
    cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None
) -> Tuple[int, str, str]:
    """Execute command and return returncode, stdout, and stderr."""
    proc = subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        env=env or os.environ.copy(),
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_doctor(evidence_dir: Path) -> Tuple[bool, Dict[str, Any]]:
    """Execute doctor check to confirm tool readiness."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "entry_point_exists": ENTRY_POINT.exists(),
        "default_csv_exists": DEFAULT_CSV.exists(),
        "checks": {},
    }

    # Check 1: Python version >= 3.10
    version_ok = sys.version_info >= (3, 10)
    results["checks"]["python_version_3_10_plus"] = {
        "status": "PASS" if version_ok else "FAIL",
        "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }

    # Check 2: Entry point syntax compile
    compile_rc, compile_out, compile_err = run_command(
        [sys.executable, "-m", "py_compile", str(ENTRY_POINT)]
    )
    results["checks"]["py_compile"] = {
        "status": "PASS" if compile_rc == 0 else "FAIL",
        "exit_code": compile_rc,
        "stderr": compile_err.strip(),
    }

    # Check 3: CLI --help execution
    help_rc, help_out, help_err = run_command(
        [sys.executable, str(ENTRY_POINT), "--help"]
    )
    help_ok = help_rc == 0 and "usage:" in help_out.lower()
    results["checks"]["cli_help"] = {
        "status": "PASS" if help_ok else "FAIL",
        "exit_code": help_rc,
        "stdout_snippet": help_out.splitlines()[0] if help_out.splitlines() else "",
    }

    overall_pass = (
        version_ok
        and results["entry_point_exists"]
        and compile_rc == 0
        and help_ok
    )
    results["overall_status"] = "PASS" if overall_pass else "FAIL"

    evidence_file = evidence_dir / "doctor_evidence.json"
    evidence_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    return overall_pass, results


def drive_category_counts(temp_dir: Path) -> Dict[str, Any]:
    """Drive category counts and alphabetical sorting verification."""
    csv_path = temp_dir / "test_category_counts.csv"
    csv_path.write_text(
        CSV_HEADER
        + "T-1,2026-01-01 10:00:00,2026-01-01 11:00:00,Hardware,high,resolved\n"
        + "T-2,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"
        + "T-3,2026-01-01 10:00:00,2026-01-01 14:00:00,Billing,medium,resolved\n"
        + "T-4,2026-01-01 10:00:00,2026-01-01 15:00:00,Access,high,resolved\n",
        encoding="utf-8",
    )

    rc, stdout, stderr = run_command([sys.executable, str(ENTRY_POINT), str(csv_path)])

    checks = {
        "exit_code_zero": rc == 0,
        "contains_access_1": "Access: 1" in stdout,
        "contains_billing_2": "Billing: 2" in stdout,
        "contains_hardware_1": "Hardware: 1" in stdout,
        "alphabetical_order": (
            "Access" in stdout
            and "Billing" in stdout
            and "Hardware" in stdout
            and stdout.index("Access") < stdout.index("Billing") < stdout.index("Hardware")
        ),
    }

    passed = all(checks.values())
    return {
        "feature": "category_counts_and_sorting",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout": stdout,
        "stderr": stderr,
        "checks": checks,
    }


def drive_average_resolution_time(temp_dir: Path) -> Dict[str, Any]:
    """Drive average resolution time calculation and formatting verification."""
    csv_path = temp_dir / "test_resolution_time.csv"
    csv_path.write_text(
        CSV_HEADER
        + "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"  # 2.0 hrs
        + "T-2,2026-01-01 10:00:00,2026-01-01 16:00:00,Billing,medium,resolved\n"  # 6.0 hrs -> Billing avg 4.0h
        + "T-3,2026-01-01 10:00:00,2026-01-02 10:00:00,Hardware,high,resolved\n",  # 24.0 hrs -> Hardware avg 24.0h
        encoding="utf-8",
    )

    rc, stdout, stderr = run_command([sys.executable, str(ENTRY_POINT), str(csv_path)])

    expected_overall = "0 days, 10 hours, 40 minutes (10.67 hours)"
    expected_billing = "0 days, 4 hours, 0 minutes (4.00 hours)"
    expected_hardware = "1 day, 0 hours, 0 minutes (24.00 hours)"

    checks = {
        "exit_code_zero": rc == 0,
        "overall_average_matched": expected_overall in stdout,
        "billing_average_matched": expected_billing in stdout,
        "hardware_average_matched": expected_hardware in stdout,
    }

    passed = all(checks.values())
    return {
        "feature": "average_resolution_time",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout": stdout,
        "stderr": stderr,
        "checks": checks,
    }


def drive_row_validation_and_warnings(temp_dir: Path) -> Dict[str, Any]:
    """Drive row validation and stderr warning verification."""
    csv_path = temp_dir / "test_row_validation.csv"
    csv_path.write_text(
        CSV_HEADER
        + ",2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"  # Row 2 missing ticket_id
        + "T-99,invalid-date,2026-01-01 11:00:00,Billing,low,resolved\n"  # invalid created_at
        + "T-98,2026-01-01 10:00:00,2026-01-01 11:00:00,,low,resolved\n"  # missing category
        + "T-97,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,,resolved\n"  # missing priority
        + "T-96,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,\n"  # missing status
        + "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,high,resolved\n",  # valid
        encoding="utf-8",
    )

    rc, stdout, stderr = run_command([sys.executable, str(ENTRY_POINT), str(csv_path)])

    checks = {
        "exit_code_zero": rc == 0,
        "row_missing_ticket_id_warned": "Row 2: Missing ticket_id" in stderr,
        "invalid_created_at_warned": "T-99: Invalid or missing created_at" in stderr,
        "missing_category_warned": "T-98: Missing category" in stderr,
        "missing_priority_warned": "T-97: Missing priority" in stderr,
        "missing_status_warned": "T-96: Missing status" in stderr,
        "valid_row_counted": "Billing: 1" in stdout,
    }

    passed = all(checks.values())
    return {
        "feature": "row_validation_and_warnings",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout": stdout,
        "stderr": stderr,
        "checks": checks,
    }


def drive_skipped_tickets(temp_dir: Path) -> Dict[str, Any]:
    """Drive skipped tickets tracking and category reporting verification."""
    csv_path = temp_dir / "test_skipped_tickets.csv"
    csv_path.write_text(
        CSV_HEADER
        + "T-100,2026-01-01 10:00:00,2026-01-01 12:00:00,DevOps,high,resolved\n"  # valid resolved
        + "T-101,2026-01-01 10:00:00,,DevOps,low,open\n"  # missing resolution date
        + "T-102,2026-01-02 10:00:00,2026-01-01 10:00:00,DevOps,medium,resolved\n"  # resolved before created
        + "T-103,2026-01-01 10:00:00,corrupted-date,DevOps,low,resolved\n"  # invalid resolved_at
        + "T-104,2026-01-01 10:00:00,2026-01-01 12:00:00,DevOps,low,in_progress\n",  # non-resolved status
        encoding="utf-8",
    )

    rc, stdout, stderr = run_command([sys.executable, str(ENTRY_POINT), str(csv_path)])

    checks = {
        "exit_code_zero": rc == 0,
        "resolved_before_created_warned": "T-102: Resolved date earlier than created date" in stderr,
        "invalid_resolved_date_warned": "T-103: Invalid resolved_at timestamp" in stderr,
        "skipped_section_present": "Skipped Tickets (Resolution Time):" in stdout,
        "missing_date_reported": "Unresolved / Missing resolution date: T-101" in stdout,
        "non_resolved_status_reported": "Unresolved / Non-resolved status: T-104" in stdout,
        "resolved_before_created_reported": "Resolved before created: T-102" in stdout,
        "invalid_date_reported": "Invalid resolution date: T-103" in stdout,
        "only_valid_resolved_counted_in_avg": "0 days, 2 hours, 0 minutes (2.00 hours)" in stdout,
        "all_valid_tickets_counted_in_category": "DevOps: 5" in stdout,
    }

    passed = all(checks.values())
    return {
        "feature": "skipped_tickets_tracking",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout": stdout,
        "stderr": stderr,
        "checks": checks,
    }


def drive_json_output_mode(temp_dir: Path) -> Dict[str, Any]:
    """Drive JSON output mode verification."""
    csv_path = temp_dir / "test_json_mode.csv"
    csv_path.write_text(
        CSV_HEADER
        + ",2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved\n"  # malformed row 2
        + "T-1,2026-01-01 10:00:00,2026-01-01 12:00:00,Billing,low,resolved\n"  # 2.0h
        + "T-2,2026-01-01 10:00:00,,Hardware,high,open\n",  # unresolved
        encoding="utf-8",
    )

    rc, stdout, stderr = run_command(
        [sys.executable, str(ENTRY_POINT), str(csv_path), "--json"]
    )

    valid_json = False
    parsed: Dict[str, Any] = {}
    try:
        parsed = json.loads(stdout)
        valid_json = True
    except Exception:
        valid_json = False

    checks = {
        "exit_code_zero": rc == 0,
        "warning_on_stderr_only": "Row 2: Missing ticket_id" in stderr,
        "stdout_is_valid_json": valid_json,
        "has_category_counts": valid_json and "category_counts" in parsed and parsed["category_counts"].get("Billing") == 1,
        "has_overall_average": valid_json and parsed.get("overall_average_resolution_time") == "0 days, 2 hours, 0 minutes (2.00 hours)",
        "has_hardware_na": valid_json and parsed.get("categories", {}).get("Hardware", {}).get("average_resolution_time") == "N/A (No resolved tickets)",
        "has_skipped_ticket": valid_json and "T-2" in parsed.get("skipped_tickets", {}).get("Unresolved / Missing resolution date", []),
    }

    passed = all(checks.values())
    return {
        "feature": "json_output_mode",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout": stdout,
        "stderr": stderr,
        "checks": checks,
    }


def drive_fatal_input_validation(temp_dir: Path) -> Dict[str, Any]:
    """Drive fatal input validation: non-existent file, directory, empty file, missing headers."""
    # 1. Non-existent file
    rc_missing, _, err_missing = run_command(
        [sys.executable, str(ENTRY_POINT), str(temp_dir / "does_not_exist.csv")]
    )
    # 2. Directory passed
    rc_dir, _, err_dir = run_command(
        [sys.executable, str(ENTRY_POINT), str(temp_dir)]
    )
    # 3. Empty file
    empty_csv = temp_dir / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")
    rc_empty, _, err_empty = run_command(
        [sys.executable, str(ENTRY_POINT), str(empty_csv)]
    )
    # 4. Missing headers
    bad_headers_csv = temp_dir / "bad_headers.csv"
    bad_headers_csv.write_text("ticket_id,category\n", encoding="utf-8")
    rc_headers, _, err_headers = run_command(
        [sys.executable, str(ENTRY_POINT), str(bad_headers_csv)]
    )

    checks = {
        "missing_file_rejected": rc_missing == 1 and "does not exist" in err_missing,
        "directory_rejected": rc_dir == 1 and "is a directory" in err_dir,
        "empty_file_rejected": rc_empty == 1 and "is empty" in err_empty,
        "missing_headers_rejected": rc_headers == 1 and "Missing required column" in err_headers,
    }

    passed = all(checks.values())
    return {
        "feature": "fatal_input_validation",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
    }


def drive_real_dataset() -> Dict[str, Any]:
    """Drive verification against the repository default tickets.csv."""
    rc, stdout, stderr = run_command(
        [sys.executable, str(ENTRY_POINT), str(DEFAULT_CSV)]
    )

    checks = {
        "exit_code_zero": rc == 0,
        "contains_row_warnings": "Warning: TCK-1183: Invalid or missing created_at." in stderr,
        "contains_chrono_warning": "Warning: TCK-1137: Resolved date earlier than created date." in stderr,
        "contains_category_table": "Tickets by Category:" in stdout,
        "contains_skipped_section": "Skipped Tickets (Resolution Time):" in stdout,
        "overall_average_present": "Average Resolution Time:" in stdout,
    }

    passed = all(checks.values())
    return {
        "feature": "real_dataset_tickets_csv",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout_snippet": "\n".join(stdout.splitlines()[:15]),
        "stderr_snippet": "\n".join(stderr.splitlines()[:10]),
        "checks": checks,
    }


def drive_excel_data_anomalies(temp_dir: Path) -> Dict[str, Any]:
    """Drive cross-verification of Excel data anomalies:
    1. Slash dates (DD/MM/YYYY) and impossible dates (Feb 30).
    2. Category casing variants (Billing * 3: Billing, billing, BILLING).
    3. Compound comma category ('Billing, refunds').
    4. Extra column ('note: sent by phone') and non-standard status ('escalatd').
    """
    csv_path = temp_dir / "test_excel_anomalies.csv"
    csv_content = (
        CSV_HEADER
        # 1. Billing casing variants (* 3)
        + "T-B1,2026-02-01 10:00:00,2026-02-01 12:00:00,Billing,normal,resolved\n"
        + "T-B2,2026-02-01 10:00:00,2026-02-01 13:00:00,billing,normal,resolved\n"
        + "T-B3,2026-02-01 10:00:00,2026-02-01 14:00:00,BILLING,normal,resolved\n"
        # 2. Compound category with comma
        + 'T-C1,2026-02-01 10:00:00,,"Billing, refunds",low,open\n'
        # 3. Date anomalies: slash date and impossible calendar date
        + "T-D1,02/03/2026 10:02,03/03/2026 10:09,Shipping,normal,resolved\n"
        + "T-D2,2026-02-30 10:00,,Refunds,normal,in_progress\n"
        # 4. Extra column and non-standard status 'escalatd'
        + "T-E1,2026-02-01 10:00:00,,Billing,normal,escalatd\n"
        + "T-E2,2026-02-01 10:00:00,,Refunds,normal,open,note: sent by phone\n"
    )
    csv_path.write_text(csv_content, encoding="utf-8")

    rc, stdout, stderr = run_command([sys.executable, str(ENTRY_POINT), str(csv_path)])

    checks = {
        "exit_code_zero": rc == 0,
        # 1. Date anomalies flagged on stderr
        "slash_date_warned": "T-D1: Invalid or missing created_at" in stderr,
        "impossible_date_warned": "T-D2: Invalid or missing created_at" in stderr,
        # 2. Billing casing normalized into unified Billing
        "billing_normalized_count": "Billing: 4" in stdout,
        "billing_lower_not_separate": "billing: 1" not in stdout,
        "billing_upper_not_separate": "BILLING: 1" not in stdout,
        # 3. Compound category parsed without CSV delimiter crash
        "compound_category_counted": "Billing, refunds: 1" in stdout,
        # 4. Resolved, Escalated, and Note sections present
        "resolved_section_present": "Resolved Tickets:" in stdout and "T-B1" in stdout,
        "escalated_section_present": "Escalated Tickets:" in stdout and "T-E1" in stdout,
        "notes_section_present": "Ticket Notes:" in stdout and "T-E2: note: sent by phone" in stdout,
    }

    # Cross-verify against the repository's real tickets.csv
    rc_real, stdout_real, stderr_real = run_command(
        [sys.executable, str(ENTRY_POINT), str(DEFAULT_CSV)]
    )
    checks["real_dataset_has_unified_billing"] = "Billing: 40" in stdout_real
    checks["real_dataset_has_no_upper_billing"] = "BILLING: 1" not in stdout_real
    checks["real_dataset_has_no_lower_billing"] = "billing: 1" not in stdout_real
    checks["real_dataset_has_compound_cat"] = "Billing, refunds: 1" in stdout_real
    checks["real_dataset_warns_slash_date"] = "Warning: TCK-1021: Invalid or missing created_at." in stderr_real
    checks["real_dataset_warns_feb_30"] = "Warning: TCK-1025: Invalid or missing created_at." in stderr_real
    checks["real_dataset_has_escalated_section"] = "Escalated Tickets:" in stdout_real and "TCK-1009" in stdout_real
    checks["real_dataset_has_resolved_section"] = "Resolved Tickets:" in stdout_real and "TCK-1012" in stdout_real
    checks["real_dataset_has_ticket_notes"] = "Ticket Notes:" in stdout_real and "TCK-2999: note: sent by phone" in stdout_real

    passed = all(checks.values())
    return {
        "feature": "excel_data_anomalies",
        "status": "PASS" if passed else "FAIL",
        "exit_code": rc,
        "stdout": stdout,
        "stderr": stderr,
        "checks": checks,
    }


def main() -> int:
    """CLI orchestrator for verification skill."""
    parser = argparse.ArgumentParser(
        description="Verification harness for Python Ticket Summary CLI tool."
    )
    parser.add_argument(
        "action",
        choices=["doctor", "drive", "all"],
        nargs="?",
        default="all",
        help="Verification action to perform.",
    )
    parser.add_argument(
        "--feature",
        choices=[
            "category-counts",
            "resolution-time",
            "row-validation",
            "skipped-tickets",
            "json-mode",
            "fatal-input",
            "real-dataset",
            "excel-anomalies",
        ],
        help="Specific feature to drive when action is 'drive'.",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
        help="Path where persistent evidence artifacts are stored.",
    )

    args = parser.parse_args()
    evidence_dir = args.evidence_dir
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting verification action: '{args.action}'")
    print(f"[*] Evidence directory: {evidence_dir}")

    # 1. Doctor
    if args.action in ("doctor", "all"):
        doctor_pass, doctor_results = run_doctor(evidence_dir)
        print(f"[+] Doctor status: {'PASS' if doctor_pass else 'FAIL'}")
        if not doctor_pass and args.action != "all":
            return 1

    # 2. Drive features
    feature_results: List[Dict[str, Any]] = []
    if args.action in ("drive", "all"):
        temp_scratch = Path(tempfile.mkdtemp(prefix="ticket_verify_"))
        try:
            feature_targets = [args.feature] if args.feature else [
                "category-counts",
                "resolution-time",
                "row-validation",
                "skipped-tickets",
                "json-mode",
                "fatal-input",
                "real-dataset",
                "excel-anomalies",
            ]

            for feat in feature_targets:
                print(f"[*] Driving feature: {feat}...")
                if feat == "category-counts":
                    res = drive_category_counts(temp_scratch)
                elif feat == "resolution-time":
                    res = drive_average_resolution_time(temp_scratch)
                elif feat == "row-validation":
                    res = drive_row_validation_and_warnings(temp_scratch)
                elif feat == "skipped-tickets":
                    res = drive_skipped_tickets(temp_scratch)
                elif feat == "json-mode":
                    res = drive_json_output_mode(temp_scratch)
                elif feat == "fatal-input":
                    res = drive_fatal_input_validation(temp_scratch)
                elif feat == "real-dataset":
                    res = drive_real_dataset()
                elif feat == "excel-anomalies":
                    res = drive_excel_data_anomalies(temp_scratch)
                else:
                    continue

                feature_results.append(res)
                print(f"    -> Status: {res['status']}")
        finally:
            # Cleanup temporary scratch files
            if temp_scratch.exists():
                shutil.rmtree(temp_scratch, ignore_errors=True)

    # 3. Write summary evidence
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": args.action,
        "feature_results": feature_results,
        "overall_status": (
            "PASS"
            if all(f["status"] == "PASS" for f in feature_results)
            else "FAIL"
        ),
    }

    summary_file = evidence_dir / "run_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[+] Evidence preserved at: {summary_file}")

    # Confirm evidence exists after cleanup
    if not summary_file.exists():
        print("[-] Error: Evidence file was deleted during cleanup!", file=sys.stderr)
        return 1

    all_passed = summary["overall_status"] == "PASS"
    print(f"[*] Overall verification result: {'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
