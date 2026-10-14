"""Ticket summary CLI tool."""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
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

RESOLVED_STATUSES = {"resolved", "closed"}
ESCALATED_STATUSES = {"escalated", "escalatd"}


def _is_simple_casing(s: str) -> bool:
    """Return True if string is entirely lowercase, uppercase, or capitalized."""
    return s.islower() or s.isupper() or s == s.capitalize()


def build_canonical_category_map(rows: List[Dict[str, str]]) -> Dict[str, str]:
    """Build case-insensitive category map preferring mixed-case/title-case forms."""
    canonical: Dict[str, str] = {}
    for row in rows:
        trimmed = row.get("category", "").strip()
        if not trimmed:
            continue
        key = trimmed.lower()
        if key not in canonical:
            canonical[key] = (
                trimmed.capitalize()
                if (trimmed.islower() or trimmed.isupper())
                else trimmed
            )
        else:
            existing = canonical[key]
            if _is_simple_casing(existing) and not _is_simple_casing(trimmed):
                canonical[key] = trimmed
    return canonical


@dataclass
class TicketMetrics:
    """Computed ticket summary metrics."""

    category_counts: Counter
    overall_average_seconds: Optional[float]
    category_average_seconds: Dict[str, Optional[float]]
    skipped_tickets: Dict[str, List[str]]
    resolved_tickets: List[str]
    escalated_tickets: List[str]
    ticket_notes: Dict[str, str]


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


def format_duration(seconds: Optional[float]) -> str:
    """Format duration in seconds into human-readable duration string."""
    if seconds is None:
        return "N/A (No resolved tickets)"

    total_hours = seconds / 3600.0
    total_sec = round(seconds)

    days = total_sec // 86400
    rem_sec = total_sec % 86400
    hours = rem_sec // 3600
    rem_sec = rem_sec % 3600
    minutes = rem_sec // 60

    days_label = f"{days} day" if days == 1 else f"{days} days"
    hours_label = f"{hours} hour" if hours == 1 else f"{hours} hours"
    minutes_label = f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"

    formatted_str = f"{days_label}, {hours_label}, {minutes_label}"
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
            seen_ticket_ids: set = set()

            note_col_idx = None
            for idx, h in enumerate(clean_headers):
                if h.lower() in {"note", "notes"}:
                    note_col_idx = idx
                    break

            for row_idx, row in enumerate(reader, start=2):
                if not row or not any(cell.strip() for cell in row):
                    continue

                padded_row = row + [""] * (len(clean_headers) - len(row))
                row_dict = {
                    h: padded_row[idx].strip() for idx, h in enumerate(clean_headers)
                }
                extra_cols = [c.strip() for c in row[len(clean_headers) :] if c.strip()]
                header_note = (
                    padded_row[note_col_idx].strip() if note_col_idx is not None else ""
                )
                all_notes = ([header_note] if header_note else []) + extra_cols
                if all_notes:
                    row_dict["_extra_note"] = ", ".join(all_notes)

                ticket_id = row_dict.get("ticket_id", "").strip()
                if not ticket_id:
                    row_warnings.append(f"Warning: Row {row_idx}: Missing ticket_id.")
                    continue

                if ticket_id.upper() in {"N/A", "NA", "NONE", "NULL"}:
                    row_warnings.append(
                        f"Warning: Row {row_idx}: Invalid ticket_id '{ticket_id}'."
                    )
                    continue

                if ticket_id in seen_ticket_ids:
                    row_warnings.append(
                        f"Warning: {ticket_id}: Duplicate ticket ID (skipped)."
                    )
                    continue

                category = row_dict.get("category", "").strip()
                if not category:
                    row_warnings.append(f"Warning: {ticket_id}: Missing category.")
                    continue

                priority = row_dict.get("priority", "").strip()
                if not priority:
                    row_warnings.append(f"Warning: {ticket_id}: Missing priority.")
                    continue

                status = row_dict.get("status", "").strip()
                if not status:
                    row_warnings.append(f"Warning: {ticket_id}: Missing status.")
                    continue

                created_str = row_dict.get("created_at", "").strip()
                created_dt = parse_iso_timestamp(created_str)
                if not created_str or created_dt is None:
                    row_warnings.append(
                        f"Warning: {ticket_id}: Invalid or missing created_at."
                    )
                    continue

                valid_rows.append(row_dict)
                seen_ticket_ids.add(ticket_id)

            return valid_rows, [], row_warnings

    except Exception as exc:
        return [], [f"Error reading '{file_path}': {exc}"], []


def compute_metrics(
    rows: List[Dict[str, str]],
) -> Tuple[TicketMetrics, List[str]]:
    """Compute category counts, resolution metrics, and track skipped tickets.

    Returns:
        Tuple of (TicketMetrics, resolution_warnings)
    """
    canonical_categories = build_canonical_category_map(rows)

    category_counts: Counter = Counter()
    category_durations: Dict[str, List[float]] = defaultdict(list)
    all_durations: List[float] = []

    skipped_tickets: Dict[str, List[str]] = defaultdict(list)
    resolved_tickets: List[str] = []
    escalated_tickets: List[str] = []
    ticket_notes: Dict[str, str] = {}
    resolution_warnings: List[str] = []

    for row in rows:
        ticket_id = row.get("ticket_id", "")
        raw_cat = row.get("category", "Uncategorized").strip()
        category = canonical_categories.get(
            raw_cat.lower(), raw_cat if raw_cat else "Uncategorized"
        )
        category_counts[category] += 1

        created_dt = parse_iso_timestamp(row.get("created_at", ""))
        resolved_str = row.get("resolved_at", "").strip()
        raw_status = row.get("status", "").strip()
        status = raw_status.lower()

        # Track escalated status explicitly
        if status in ESCALATED_STATUSES:
            escalated_tickets.append(ticket_id)

        # Track resolved tickets based on resolved status
        if status in RESOLVED_STATUSES:
            resolved_tickets.append(ticket_id)

        # Track notes from extra columns or note fields
        if "_extra_note" in row:
            ticket_notes[ticket_id] = row["_extra_note"]

        if not resolved_str:
            skipped_tickets["Unresolved / Missing resolution date"].append(ticket_id)
            continue

        if status not in RESOLVED_STATUSES:
            skipped_tickets["Unresolved / Non-resolved status"].append(ticket_id)
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
                f"Warning: {ticket_id}: Resolved date earlier than created date."
            )
            skipped_tickets["Resolved before created"].append(ticket_id)
            continue

        if created_dt and resolved_dt >= created_dt:
            dur_seconds = (resolved_dt - created_dt).total_seconds()
            all_durations.append(dur_seconds)
            category_durations[category].append(dur_seconds)

    overall_avg_sec = sum(all_durations) / len(all_durations) if all_durations else None

    category_averages: Dict[str, Optional[float]] = {}
    for category in sorted(category_counts.keys()):
        durations = category_durations.get(category, [])
        category_averages[category] = (
            sum(durations) / len(durations) if durations else None
        )

    metrics = TicketMetrics(
        category_counts=category_counts,
        overall_average_seconds=overall_avg_sec,
        category_average_seconds=category_averages,
        skipped_tickets=skipped_tickets,
        resolved_tickets=resolved_tickets,
        escalated_tickets=escalated_tickets,
        ticket_notes=ticket_notes,
    )
    return metrics, resolution_warnings


def format_summary_text(metrics: TicketMetrics) -> str:
    """Format ticket metrics into clean text output."""
    overall_avg_str = format_duration(metrics.overall_average_seconds)

    lines: List[str] = [
        "Ticket Summary",
        "==============",
        f"Average Resolution Time: {overall_avg_str}",
        "",
        "Tickets by Category:",
    ]

    for category in sorted(metrics.category_counts.keys()):
        count = metrics.category_counts[category]
        cat_avg_str = format_duration(metrics.category_average_seconds.get(category))
        lines.append(f"  {category}: {count} (Avg Resolution: {cat_avg_str})")

    if metrics.resolved_tickets:
        lines.append("")
        lines.append("Resolved Tickets:")
        lines.append(f"  {', '.join(metrics.resolved_tickets)}")

    if metrics.escalated_tickets:
        lines.append("")
        lines.append("Escalated Tickets:")
        lines.append(f"  {', '.join(metrics.escalated_tickets)}")

    if metrics.ticket_notes:
        lines.append("")
        lines.append("Ticket Notes:")
        for tid in sorted(metrics.ticket_notes.keys()):
            lines.append(f"  {tid}: {metrics.ticket_notes[tid]}")

    if metrics.skipped_tickets:
        lines.append("")
        lines.append("Skipped Tickets (Resolution Time):")
        preferred_reasons = [
            "Unresolved / Missing resolution date",
            "Unresolved / Non-resolved status",
            "Resolved before created",
            "Invalid resolution date",
        ]
        all_reasons = preferred_reasons + [
            r
            for r in sorted(metrics.skipped_tickets.keys())
            if r not in preferred_reasons
        ]
        for reason in all_reasons:
            ticket_ids = metrics.skipped_tickets.get(reason, [])
            if ticket_ids:
                ticket_ids_str = ", ".join(ticket_ids)
                lines.append(f"  {reason}: {ticket_ids_str}")

    return "\n".join(lines)


def format_summary_json(metrics: TicketMetrics) -> str:
    """Format ticket metrics into machine-readable JSON."""
    categories_detail = {}
    for category in sorted(metrics.category_counts.keys()):
        categories_detail[category] = {
            "count": metrics.category_counts[category],
            "average_resolution_time": format_duration(
                metrics.category_average_seconds.get(category)
            ),
        }

    payload = {
        "category_counts": dict(sorted(metrics.category_counts.items())),
        "overall_average_resolution_time": format_duration(
            metrics.overall_average_seconds
        ),
        "categories": categories_detail,
        "resolved_tickets": metrics.resolved_tickets,
        "escalated_tickets": metrics.escalated_tickets,
        "ticket_notes": metrics.ticket_notes,
        "skipped_tickets": dict(metrics.skipped_tickets),
    }
    return json.dumps(payload, indent=2)


def process_tickets(file_path: Path, output_json: bool = False) -> int:
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

    if output_json:
        print(format_summary_json(metrics))
    else:
        print(format_summary_text(metrics))
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output summary as structured JSON.",
    )
    args = parser.parse_args(argv)
    return process_tickets(args.file, output_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
