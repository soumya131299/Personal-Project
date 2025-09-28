from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Iterable, Optional


@dataclass
class MessageMeta:
	uid: int
	folder: str
	fetched_at: str
	size: int


class FileSystemStorage:
	"""Simple filesystem storage for raw emails and per-account metadata.

	Structure:
	- base_dir/
	  - raw/<account>/<uid>.eml
	  - meta/<account>.jsonl  (one JSON object per line)
	"""

	def __init__(self, base_dir: Path | str) -> None:
		self.base_dir = Path(base_dir)
		(self.base_dir / "raw").mkdir(parents=True, exist_ok=True)
		(self.base_dir / "meta").mkdir(parents=True, exist_ok=True)

	def _meta_path(self, account: str) -> Path:
		return self.base_dir / "meta" / f"{account}.jsonl"

	def _raw_dir(self, account: str) -> Path:
		d = self.base_dir / "raw" / account
		d.mkdir(parents=True, exist_ok=True)
		return d

	def append_meta(self, account: str, meta: MessageMeta) -> None:
		p = self._meta_path(account)
		with p.open("a", encoding="utf-8") as f:
			f.write(json.dumps(meta.__dict__) + "\n")

	def list_meta(self, account: str) -> Iterable[MessageMeta]:
		p = self._meta_path(account)
		if not p.exists():
			return []
		with p.open("r", encoding="utf-8") as f:
			for line in f:
				try:
					d = json.loads(line)
					yield MessageMeta(**d)
				except Exception:
					continue

	def highest_uid(self, account: str) -> Optional[int]:
		max_uid: Optional[int] = None
		for m in self.list_meta(account):
			if max_uid is None or m.uid > max_uid:
				max_uid = m.uid
		return max_uid

	def save_raw(self, account: str, uid: int, content: bytes) -> Path:
		path = self._raw_dir(account) / f"{uid}.eml"
		with path.open("wb") as f:
			f.write(content)
		return path

	@staticmethod
	def build_meta(uid: int, folder: str, size: int) -> MessageMeta:
		return MessageMeta(
			uid=uid,
			folder=folder,
			size=size,
			fetched_at=datetime.now(timezone.utc).isoformat(),
		)

