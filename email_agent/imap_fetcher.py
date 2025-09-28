from __future__ import annotations
import imaplib
from typing import Generator, Iterable, Optional, Tuple


class ImapFetcher:
	def __init__(self, host: str, username: str, password: str, port: int = 993, use_ssl: bool = True, timeout: int = 30) -> None:
		self.host = host
		self.username = username
		self.password = password
		self.port = port
		self.use_ssl = use_ssl
		self.timeout = timeout

	def _connect(self) -> imaplib.IMAP4:
		imaplib._MAXLINE = max(10_000_000, imaplib._MAXLINE)  # allow large emails
		if self.use_ssl:
			client = imaplib.IMAP4_SSL(self.host, self.port)
		else:
			client = imaplib.IMAP4(self.host, self.port)
		client.login(self.username, self.password)
		return client

	def fetch_since(self, folder: str, since_uid: Optional[int]) -> Iterable[Tuple[int, bytes]]:
		client = self._connect()
		try:
			status, _ = client.select(folder)
			if status != "OK":
				return []

			if since_uid is None:
				status, data = client.uid("SEARCH", None, "ALL")
			else:
				range_expr = f"{since_uid + 1}:*"
				status, data = client.uid("SEARCH", None, f"UID {range_expr}")
			if status != "OK" or not data or not data[0]:
				return []

			uids = [int(x) for x in data[0].split()]
			if not uids:
				return []

			for uid in uids:
				status, msg_data = client.uid("FETCH", str(uid), "(RFC822)")
				if status != "OK" or not msg_data:
					continue
				raw = msg_data[0][1]
				yield uid, raw
		finally:
			try:
				client.logout()
			except Exception:
				pass

