"""Ticket summary CLI tool."""

import argparse
import csv
import sys
from collections import Counter
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


def read_and_validate_csv(
    file_path: Path,
) -> Tuple[List[Dict[str, str]], List[str]]:
    """Read CSV file, validate required headers, and trim whitespace.

    Returns:
        Tuple of (valid_rows, error_messages)
    """
    if not file_path.exists():
        return [], [f"Error: File '{file_path}' does not exist."]

    if file_path.is_dir():
        return [], [f"Error: Path '{file_path}' is a directory, not a file."]

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header_row = next(reader, None)

            if header_row is None:
                return [], [f"Error: File '{file_path}' is empty."]

            clean_headers = [col.strip() for col in header_row]
            missing_cols = REQUIRED_COLUMNS - set(clean_headers)
            if missing_cols:
                missing_str = ", ".join(sorted(missing_cols))
                return [], [f"Error: Missing required column(s): {missing_str}."]

            rows: List[Dict[str, str]] = []
            for row in reader:
                # Skip empty lines
                if not row or not any(cell.strip() for cell in row):
                    continue
                # Map row to headers
                padded_row = row + [""] * (len(clean_headers) - len(row))
                row_dict = {
                    h: padded_row[idx].strip() for idx, h in enumerate(clean_headers)
                }
                rows.append(row_dict)

            return rows, []
    except Exception as exc:
        return [], [f"Error reading '{file_path}': {exc}"]


def format_summary_text(
    category_counts: Dict[str, int],
    total_tickets: int,
) -> str:
    """Format category breakdown into clean text output."""
    lines: List[str] = [
        "Ticket Summary",
        "==============",
        f"Total Tickets: {total_tickets}",
        "",
        "Tickets by Category:",
    ]
    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        lines.append(f"  {category}: {count}")

    return "\n".join(lines)


def process_tickets(file_path: Path) -> int:
    """Core processor for ticket CSV file."""
    rows, errors = read_and_validate_csv(file_path)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    category_counts = Counter(row.get("category", "Uncategorized") for row in rows)
    output = format_summary_text(category_counts, len(rows))
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
