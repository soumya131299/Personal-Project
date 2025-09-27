import csv
import os
import sys
from dataclasses import asdict
from typing import List

try:
	from dotenv import load_dotenv  # optional
except Exception:  # ImportError or any failure
	def load_dotenv() -> None:
		return None

from .extractors import extract_from_parts
from .imap_client import fetch_luma_emails


def main() -> int:
	load_dotenv()
	imap_host = os.getenv("IMAP_HOST")
	imap_user = os.getenv("IMAP_USER")
	imap_pass = os.getenv("IMAP_PASS")
	mailbox = os.getenv("IMAP_MAILBOX", "INBOX")
	limit_env = os.getenv("IMAP_LIMIT")
	limit = int(limit_env) if limit_env else None
	outfile = os.getenv("OUTPUT_CSV", "luma_contacts.csv")

	for var, name in [(imap_host, "IMAP_HOST"), (imap_user, "IMAP_USER"), (imap_pass, "IMAP_PASS")]:
		if not var:
			print(f"Missing required environment variable: {name}", file=sys.stderr)
			return 2

	rows: List[dict] = []
	for item in fetch_luma_emails(imap_host, imap_user, imap_pass, mailbox=mailbox, limit=limit):
		data = extract_from_parts([*item.text_parts, *item.html_parts])
		rows.append({
			"date": item.date,
			"from": item.from_addr,
			"subject": item.subject,
			"linkedin_urls": ";".join(data["linkedin_urls"]),
			"phone_numbers": ";".join(data["phone_numbers"]),
		})

	fieldnames = ["date", "from", "subject", "linkedin_urls", "phone_numbers"]
	with open(outfile, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for r in rows:
			writer.writerow(r)

	print(f"Wrote {len(rows)} rows to {outfile}")
	return 0


if __name__ == "__main__":
\tsys.exit(main())

