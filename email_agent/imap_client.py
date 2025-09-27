import email
import imaplib
import os
from dataclasses import dataclass
from email.message import Message
from typing import Generator, List, Optional, Tuple


LUMA_SENDER_HINTS = [
	"luma",  # luma, luma.events
	"@luma",  # domains containing luma
]

LUMA_KEYWORDS = [
	"luma",
	"rsvp",
	"event",
	"ticket",
]


@dataclass
class EmailContent:
	subject: str
	from_addr: str
	date: str
	text_parts: List[str]
	html_parts: List[str]


def _match_luma(from_addr: str, subject: str, preview: str) -> bool:
	low_from = (from_addr or "").lower()
	low_subj = (subject or "").lower()
	low_prev = (preview or "").lower()
	if any(h in low_from for h in LUMA_SENDER_HINTS):
		return True
	return any(k in low_subj for k in LUMA_KEYWORDS) or any(k in low_prev for k in LUMA_KEYWORDS)


def _get_bodies(msg: Message) -> Tuple[List[str], List[str]]:
	text_parts: List[str] = []
	html_parts: List[str] = []
	if msg.is_multipart():
		for part in msg.walk():
			ctype = part.get_content_type()
			if ctype in ("text/plain", "text/html"):
				try:
					payload = part.get_payload(decode=True) or b""
					charset = part.get_content_charset() or "utf-8"
					text = payload.decode(charset, errors="replace")
					if ctype == "text/plain":
						text_parts.append(text)
					else:
						html_parts.append(text)
				except Exception:
					continue
	else:
		try:
			payload = msg.get_payload(decode=True) or b""
			charset = msg.get_content_charset() or "utf-8"
			text = payload.decode(charset, errors="replace")
			if msg.get_content_type() == "text/html":
				html_parts.append(text)
			else:
				text_parts.append(text)
		except Exception:
			pass
	return text_parts, html_parts


def fetch_luma_emails(
	host: str,
	username: str,
	password: str,
	mailbox: str = "INBOX",
	ssl: bool = True,
	limit: Optional[int] = None,
) -> Generator[EmailContent, None, None]:
	"""Yield Luma-related emails from an IMAP mailbox."""
	imap: Optional[imaplib.IMAP4] = None
	try:
		imap = imaplib.IMAP4_SSL(host) if ssl else imaplib.IMAP4(host)
		imap.login(username, password)
		imap.select(mailbox)

		# Search recent emails first
		status, data = imap.search(None, "ALL")
		if status != "OK":
			return

		ids = data[0].split()
		ids = list(reversed(ids))  # newest first
		if limit is not None:
			ids = ids[:limit]

		for eid in ids:
			status, msg_data = imap.fetch(eid, "(RFC822)")
			if status != "OK" or not msg_data:
				continue
			raw = msg_data[0][1]
			msg = email.message_from_bytes(raw)

			subject = msg.get("Subject", "")
			from_addr = msg.get("From", "")
			date = msg.get("Date", "")
			text_parts, html_parts = _get_bodies(msg)
			preview = (text_parts[0] if text_parts else html_parts[0] if html_parts else "")[:500]

			if not _match_luma(from_addr, subject, preview):
				continue

			yield EmailContent(
				subject=subject,
				from_addr=from_addr,
				date=date,
				text_parts=text_parts,
				html_parts=html_parts,
			)
	finally:
		try:
			if imap is not None:
				imap.logout()
		except Exception:
			pass

