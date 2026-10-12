"""Ticket summary CLI tool."""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = {
    "ticket_id",
    "created_at",
    "resolved_at",
    "category",
    "priority",
    "status",
}


def parse_iso_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse standard ISO-8601 timestamp and normalize to UTC."""
    if not ts_str or not ts_str.strip():
        return None
    cleaned = ts_str.strip()
    try:
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def format_duration(seconds: float) -> str:
    """Format duration in seconds into human-readable duration string."""
    total_hours = seconds / 3600.0
    total_sec = round(seconds)

    days = total_sec // 86400
    rem_sec = total_sec % 86400
    hours = rem_sec // 3600
    rem_sec = rem_sec % 3600
    minutes = rem_sec // 60

    parts: List[str] = []
    if days > 0:
        parts.append(f"{days} day" if days == 1 else f"{days} days")
    parts.append(f"{hours} hour" if hours == 1 else f"{hours} hours")
    parts.append(f"{minutes} minute" if minutes == 1 else f"{minutes} minutes")

    formatted_str = ", ".join(parts)
    return f"{formatted_str} ({total_hours:.2f} hours)"


def read_and_validate_csv(
    file_path: Path,
) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
    """Read CSV file, validate headers, trim whitespace, and validate rows.

    Returns:
        Tuple of (valid_rows, fatal_errors, row_warnings)
    """
    if not file_path.exists():
        return [], [f"Error: File '{file_path}' does not exist."], []

    if file_path.is_dir():
        return (
            [],
            [f"Error: Path '{file_path}' is a directory, not a file."],
            [],
        )

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header_row = next(reader, None)

            if header_row is None:
                return [], [f"Error: File '{file_path}' is empty."], []

            clean_headers = [col.strip() for col in header_row]
            missing_cols = REQUIRED_COLUMNS - set(clean_headers)
            if missing_cols:
                missing_str = ", ".join(sorted(missing_cols))
                return (
                    [],
                    [f"Error: Missing required column(s): {missing_str}."],
                    [],
                )

            valid_rows: List[Dict[str, str]] = []
            row_warnings: List[str] = []

            for row_idx, row in enumerate(reader, start=2):
                # Skip completely blank lines
                if not row or not any(cell.strip() for cell in row):
                    continue

                padded_row = row + [""] * (len(clean_headers) - len(row))
                row_dict = {
                    h: padded_row[idx].strip() for idx, h in enumerate(clean_headers)
                }

                ticket_id = row_dict.get("ticket_id", "").strip()
                if not ticket_id:
                    row_warnings.append(f"Warning: Row {row_idx}: Missing ticket_id.")
                    continue

                category = row_dict.get("category", "").strip()
                if not category:
                    row_warnings.append(f"Warning: {ticket_id}: Missing category.")
                    continue

                created_str = row_dict.get("created_at", "").strip()
                created_dt = parse_iso_timestamp(created_str)
                if not created_str or created_dt is None:
                    row_warnings.append(
                        f"Warning: {ticket_id}: Invalid or missing created_at."
                    )
                    continue

                valid_rows.append(row_dict)

            return valid_rows, [], row_warnings
    except Exception as exc:
        return [], [f"Error reading '{file_path}': {exc}"], []


def compute_metrics(
    rows: List[Dict[str, str]],
) -> Tuple[Dict[str, object], List[str]]:
    """Compute category counts, resolution metrics, and track skipped tickets.

    Returns:
        Tuple of (metrics_dict, resolution_warnings)
    """
    category_counts = Counter(row.get("category", "Uncategorized") for row in rows)
    category_durations: Dict[str, List[float]] = defaultdict(list)
    all_durations: List[float] = []

    skipped_tickets: Dict[str, List[str]] = defaultdict(list)
    resolution_warnings: List[str] = []

    for row in rows:
        ticket_id = row.get("ticket_id", "")
        created_dt = parse_iso_timestamp(row.get("created_at", ""))
        resolved_str = row.get("resolved_at", "").strip()

        if not resolved_str:
            skipped_tickets["Unresolved / Missing resolution date"].append(ticket_id)
            continue

        resolved_dt = parse_iso_timestamp(resolved_str)
        if resolved_dt is None:
            resolution_warnings.append(
                f"Warning: {ticket_id}: Invalid resolved_at timestamp."
            )
            skipped_tickets["Invalid resolution date"].append(ticket_id)
            continue

        if created_dt and resolved_dt < created_dt:
            resolution_warnings.append(
                f"Warning: {ticket_id}: Resolved date earlier than created" " date."
            )
            skipped_tickets["Resolved before created"].append(ticket_id)
            continue

        if created_dt and resolved_dt >= created_dt:
            dur_seconds = (resolved_dt - created_dt).total_seconds()
            all_durations.append(dur_seconds)
            category = row.get("category", "Uncategorized")
            category_durations[category].append(dur_seconds)

    overall_avg_sec = sum(all_durations) / len(all_durations) if all_durations else None

    category_averages: Dict[str, Optional[float]] = {}
    for cat in sorted(category_counts.keys()):
        durs = category_durations.get(cat, [])
        category_averages[cat] = sum(durs) / len(durs) if durs else None

    metrics = {
        "total_tickets": len(rows),
        "category_counts": category_counts,
        "overall_average_seconds": overall_avg_sec,
        "category_average_seconds": category_averages,
        "skipped_tickets": skipped_tickets,
    }
    return metrics, resolution_warnings


def format_summary_text(metrics: Dict[str, object]) -> str:
    """Format ticket metrics into clean text output."""
    total_tickets = metrics["total_tickets"]
    category_counts: Counter = metrics["category_counts"]  # type: ignore
    overall_avg_sec: Optional[float] = metrics["overall_average_seconds"]  # type: ignore
    category_averages: Dict[str, Optional[float]] = metrics[
        "category_average_seconds"
    ]  # type: ignore
    skipped_tickets: Dict[str, List[str]] = metrics["skipped_tickets"]  # type: ignore

    if overall_avg_sec is not None:
        overall_avg_str = format_duration(overall_avg_sec)
    else:
        overall_avg_str = "N/A (No resolved tickets)"

    lines: List[str] = [
        "Ticket Summary",
        "==============",
        f"Total Tickets: {total_tickets}",
        f"Average Resolution Time: {overall_avg_str}",
        "",
        "Tickets by Category:",
    ]

    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        cat_avg = category_averages.get(category)
        if cat_avg is not None:
            cat_avg_str = format_duration(cat_avg)
        else:
            cat_avg_str = "N/A (No resolved tickets)"
        lines.append(f"  {category}: {count} (Avg Resolution: {cat_avg_str})")

    if skipped_tickets:
        lines.append("")
        lines.append("Skipped Tickets (Resolution Time):")
        # Define clean ordering for skip reasons
        preferred_reasons = [
            "Unresolved / Missing resolution date",
            "Resolved before created",
            "Invalid resolution date",
        ]
        all_reasons = preferred_reasons + [
            r for r in sorted(skipped_tickets.keys()) if r not in preferred_reasons
        ]
        for reason in all_reasons:
            if reason in skipped_tickets and skipped_tickets[reason]:
                tids = ", ".join(skipped_tickets[reason])
                lines.append(f"  {reason}: {tids}")

    return "\n".join(lines)


def process_tickets(file_path: Path) -> int:
    """Core processor for ticket CSV file."""
    rows, fatal_errors, row_warnings = read_and_validate_csv(file_path)
    if fatal_errors:
        for err in fatal_errors:
            print(err, file=sys.stderr)
        return 1

    for warn in row_warnings:
        print(warn, file=sys.stderr)

    metrics, resolution_warnings = compute_metrics(rows)
    for warn in resolution_warnings:
        print(warn, file=sys.stderr)

    output = format_summary_text(metrics)
    print(output)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Summarize support ticket CSV reports."
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the ticket CSV file.",
    )
    args = parser.parse_args(argv)
    return process_tickets(args.file)


if __name__ == "__main__":
    sys.exit(main())
