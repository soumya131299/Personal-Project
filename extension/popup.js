async function generate() {
  const server = document.getElementById('server').value.trim().replace(/\/$/, '');
  const query = document.getElementById('query').value.trim();
  const location = document.getElementById('location').value.trim();
  const max = parseInt(document.getElementById('max').value, 10) || 50;
  const statusEl = document.getElementById('status');

  statusEl.textContent = 'Running...';
  try {
    const resp = await fetch(`${server}/api/fetch-map`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, location: location || null, max_results: max })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed: ${resp.status}`);
    }
    const data = await resp.json();
    statusEl.textContent = `Jobs: ${data.jobs_count}`;
    const url = `${server}${data.map_url}`;
    chrome.tabs.create({ url });
  } catch (e) {
    statusEl.textContent = `Error: ${e.message}`;
  }
}

document.getElementById('run').addEventListener('click', generate);

