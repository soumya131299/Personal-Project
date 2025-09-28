from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import Optional

from .imap_fetcher import ImapFetcher
from .storage import FileSystemStorage


@dataclass
class Account:
	name: str
	host: str
	username: str
	password: str
	folder: str = "INBOX"
	port: int = 993
	use_ssl: bool = True
	poll_seconds: int = 300
	since_uid: Optional[int] = None


def load_account_from_env(prefix: str = "IMAP_") -> Account:
	name = os.getenv(f"{prefix}NAME", "default")
	host = os.getenv(f"{prefix}HOST", "")
	username = os.getenv(f"{prefix}USER", "")
	password = os.getenv(f"{prefix}PASS", "")
	folder = os.getenv(f"{prefix}MAILBOX", "INBOX")
	port = int(os.getenv(f"{prefix}PORT", "993"))
	use_ssl_env = os.getenv(f"{prefix}SSL", "true").lower()
	use_ssl = use_ssl_env not in ("0", "false", "no")
	poll_seconds = int(os.getenv("AGENT_POLL_SECONDS", "300"))
	since_uid_env = os.getenv("AGENT_SINCE_UID")
	since_uid = int(since_uid_env) if since_uid_env else None
	return Account(
		name=name,
		host=host,
		username=username,
		password=password,
		folder=folder,
		port=port,
		use_ssl=use_ssl,
		poll_seconds=poll_seconds,
		since_uid=since_uid,
	)


class Agent:
	def __init__(self, storage_dir: str = "./data") -> None:
		self.storage = FileSystemStorage(storage_dir)

	def run_once(self, account: Account) -> Optional[int]:
		fetcher = ImapFetcher(
			host=account.host,
			username=account.username,
			password=account.password,
			port=account.port,
			use_ssl=account.use_ssl,
		)
		last_uid = account.since_uid or self.storage.highest_uid(account.name)
		max_uid: Optional[int] = last_uid
		for uid, raw in fetcher.fetch_since(account.folder, last_uid):
			self.storage.save_raw(account.name, uid, raw)
			meta = self.storage.build_meta(uid, account.folder, len(raw))
			self.storage.append_meta(account.name, meta)
			if max_uid is None or uid > max_uid:
				max_uid = uid
		return max_uid

	def run_loop(self, account: Account) -> None:
		while True:
			new_uid = self.run_once(account)
			if new_uid is not None:
				account.since_uid = new_uid
			time.sleep(account.poll_seconds)

