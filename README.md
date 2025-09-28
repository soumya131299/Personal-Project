## Luma Email Agent

Fetch Luma-related emails from IMAP, extract LinkedIn URLs and phone numbers, and export to CSV. Also includes a background agent to fetch and store raw emails incrementally.

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

### Background agent

Set env vars and run in once or loop mode:

```bash
# required
export IMAP_HOST=imap.example.com
export IMAP_USER=user@example.com
export IMAP_PASS=app_password

# optional
export IMAP_MAILBOX=INBOX
export AGENT_STORAGE_DIR=./data
export AGENT_POLL_SECONDS=300

# run once
AGENT_RUN=1 AGENT_ONCE=1 python -m email_agent.cli

# run loop (background via nohup)
nohup env AGENT_RUN=1 python -m email_agent.cli >/tmp/email_agent.log 2>&1 &
```

### What counts as Luma email

The agent looks for messages where the `From` address contains `luma` or the subject/body includes keywords like `luma`, `rsvp`, `event`, or `ticket`.

### Notes

- LinkedIn: Extracts personal, company, and event links.
- Phones: Extracts international-like formats; filters to at least 10 digits.
- For Gmail IMAP, enable IMAP and use an app password if 2FA is enabled.

