import csv
import os
import sys
from typing import List

try:
	from dotenv import load_dotenv  # optional
except Exception:  # ImportError or any failure
	def load_dotenv() -> None:
		return None

from .extractors import extract_from_parts
from .imap_client import fetch_luma_emails
from .agent import Agent, load_account_from_env


def main() -> int:
	load_dotenv()
	imap_host = os.getenv("IMAP_HOST")
	imap_user = os.getenv("IMAP_USER")
	imap_pass = os.getenv("IMAP_PASS")
	mailbox = os.getenv("IMAP_MAILBOX", "INBOX")
	limit_env = os.getenv("IMAP_LIMIT")
	limit = int(limit_env) if limit_env else None
	outfile = os.getenv("OUTPUT_CSV", "luma_contacts.csv")

	# Background agent mode (set AGENT_RUN=1). Runs once if AGENT_ONCE is set.
	if os.getenv("AGENT_RUN"):
		for var, name in [(imap_host, "IMAP_HOST"), (imap_user, "IMAP_USER"), (imap_pass, "IMAP_PASS")]:
			if not var:
				print(f"Missing required environment variable: {name}", file=sys.stderr)
				return 2
		storage_dir = os.getenv("AGENT_STORAGE_DIR", "./data")
		agent = Agent(storage_dir)
		account = load_account_from_env()
		if os.getenv("AGENT_ONCE"):
			agent.run_once(account)
			return 0
		else:
			agent.run_loop(account)
			return 0

	# Background agent mode (set AGENT_RUN=1). Runs once if AGENT_ONCE is set.
	if os.getenv("AGENT_RUN"):
		for var, name in [(imap_host, "IMAP_HOST"), (imap_user, "IMAP_USER"), (imap_pass, "IMAP_PASS")]:
			if not var:
				print(f"Missing required environment variable: {name}", file=sys.stderr)
				return 2
		storage_dir = os.getenv("AGENT_STORAGE_DIR", "./data")
		agent = Agent(storage_dir)
		account = load_account_from_env()
		if os.getenv("AGENT_ONCE"):
			agent.run_once(account)
			return 0
		else:
			agent.run_loop(account)
			return 0

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
	sys.exit(main())

