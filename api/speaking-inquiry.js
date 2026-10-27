// Vercel serverless function: /api/speaking-inquiry
// Sends speaking requests from /speaking to Doychin via Resend.
const TO = 'doych@doychzone.com';
const FROM = process.env.SPEAKING_FROM || 'Doychin.com Speaking <onboarding@resend.dev>';

const FIELDS = [
  ['Request type', 'request_type', true],
  ['Name', 'name', true],
  ['Email', 'email', true],
  ['Phone', 'phone'],
  ['Organization', 'organization', true],
  ['Event website', 'event_website'],
  ['Event type', 'event_type', true],
  ['Talk(s) of interest', 'topics', true],
  ['Format', 'format', true],
  ['Virtual or in person', 'delivery', true],
  ['City / venue', 'city_venue'],
  ['Event date or range', 'event_date', true],
  ['Dates flexible', 'dates_flexible'],
  ['Expected audience size', 'audience', true],
  ['Proposed speaking fee', 'fee', true],
  ['Language', 'language', true],
  ['How they heard about Doychin', 'heard_about'],
  ['About the event and goals', 'details', true],
];

const clean = (v) => {
  if (Array.isArray(v)) return v.map(clean).filter(Boolean).join('; ');
  return v == null ? '' : String(v).trim().slice(0, 5000);
};
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }
  let body = req.body || {};
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }

  // Honeypot: real visitors never fill the hidden "company_url" field.
  if (clean(body.company_url)) return res.status(200).json({ ok: true });

  const data = {};
  for (const [, k] of FIELDS) data[k] = clean(body[k]);
  const missing = FIELDS.filter(([, k, r]) => r && !data[k]).map(([l]) => l);
  if (missing.length) return res.status(400).json({ ok: false, error: 'Please complete: ' + missing.join(', ') + '.' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) return res.status(400).json({ ok: false, error: 'Please enter a valid email.' });

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(500).json({ ok: false, error: 'Email service is not configured.' });

  const subject = 'Speaking Inquiry: ' + data.organization.replace(/[\r\n]+/g, ' ');
  const rows = FIELDS.filter(([, k]) => k !== 'details');
  const text = rows.map(([l, k]) => l + ': ' + (data[k] || '-')).join('\n') + '\n\nAbout the event and goals:\n' + data.details;
  const html = '<h2 style="font-family:sans-serif">' + esc(subject) + '</h2><table style="font-family:sans-serif;border-collapse:collapse">' +
    rows.map(([l, k]) => '<tr><td style="padding:4px 12px 4px 0;color:#666;vertical-align:top">' + esc(l) + '</td><td style="padding:4px 0">' + esc(data[k] || '-') + '</td></tr>').join('') +
    '</table><h3 style="font-family:sans-serif">About the event and goals</h3><p style="font-family:sans-serif;white-space:pre-wrap">' + esc(data.details) + '</p>';

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: FROM, to: [TO], reply_to: data.email, subject, text, html }),
    });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) {
      console.error('Resend error', r.status, out && out.message);
      return res.status(502).json({ ok: false, error: 'Could not send right now.' });
    }
    return res.status(200).json({ ok: true, id: out.id });
  } catch (e) {
    console.error('Resend fetch failed', e && e.message);
    return res.status(502).json({ ok: false, error: 'Could not send right now.' });
  }
};
