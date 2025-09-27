## Luma Email Agent

Fetch Luma-related emails from IMAP, extract LinkedIn URLs and phone numbers, and export to CSV.

### Setup

1. Create a `.env` from `.env.example` and fill in credentials.
2. If you can, create a virtualenv and install deps:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

If your environment blocks venv, you can use system Python and pass `--break-system-packages` when installing, or use pipx.

### Run

```bash
python -m email_agent.cli
```

This writes `luma_contacts.csv` with columns: `date, from, subject, linkedin_urls, phone_numbers`.

### What counts as Luma email

The agent looks for messages where the `From` address contains `luma` or the subject/body includes keywords like `luma`, `rsvp`, `event`, or `ticket`.

### Notes

- LinkedIn: Extracts personal, company, and event links.
- Phones: Extracts international-like formats; filters to at least 10 digits.
- For Gmail IMAP, enable IMAP and use an app password if 2FA is enabled.

