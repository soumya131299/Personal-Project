import re
from html import unescape
from typing import Iterable, List, Set


LINKEDIN_REGEX = re.compile(
	r"https?://(?:[\w.-]*\.)?linkedin\.com/(?:in|pub|company|events)/[A-Za-z0-9%._\-+/]+",
	re.IGNORECASE,
)


# Liberal international phone pattern: captures numbers with optional +, spaces, dashes, dots, and parentheses
# Avoid matching short numbers, extensions handled with x or ext
PHONE_REGEX = re.compile(
	r"(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){1,4}\d{2,4}(?:\s?(?:x|ext)\.?\s?\d{1,6})?",
	re.IGNORECASE,
)


def _normalize_whitespace(text: str) -> str:
	return re.sub(r"\s+", " ", text).strip()


def extract_linkedin_urls(text: str) -> List[str]:
	"""Extract unique LinkedIn URLs from the provided text.

	- Matches personal profiles, companies, and events
	- Normalizes HTML entities
	- Deduplicates while preserving order
	"""
	if not text:
		return []

	decoded = unescape(text)
	matches = LINKEDIN_REGEX.findall(decoded)

	seen: Set[str] = set()
	result: List[str] = []
	for url in matches:
		url_clean = url.rstrip(').,;"\'')
		if url_clean.lower() not in seen:
			seen.add(url_clean.lower())
			result.append(url_clean)
	return result


def extract_phone_numbers(text: str) -> List[str]:
	"""Extract likely phone numbers from text.

	This aims to be generous but filters out very short matches (< 10 digits total).
	"""
	if not text:
		return []

	decoded = _normalize_whitespace(unescape(text))
	matches = PHONE_REGEX.findall(decoded)

	def digits_only(s: str) -> str:
		return re.sub(r"\D", "", s)

	seen: Set[str] = set()
	result: List[str] = []
	for raw in matches:
		candidate = raw.strip().rstrip(').,;"\'')
		digits = digits_only(candidate)
		if len(digits) < 10:
			continue
		key = digits
		if key not in seen:
			seen.add(key)
			result.append(candidate)
	return result


def extract_from_parts(parts: Iterable[str]) -> dict:
	"""Extract contacts from multiple text parts (plain text + HTML stripped segments).

	Returns a dict with keys: linkedin_urls, phone_numbers.
	"""
	all_text = "\n".join(p for p in parts if p)
	return {
		"linkedin_urls": extract_linkedin_urls(all_text),
		"phone_numbers": extract_phone_numbers(all_text),
	}

