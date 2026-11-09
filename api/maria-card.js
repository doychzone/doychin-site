// Vercel serverless function: /api/maria-card
// Receives "Leave me your details" submissions from doychzone.com/maria
// (proxied through a rewrite in the doychzone-site project) and emails them via Resend.
// Recipient comes from MARIA_CARD_TO. If it is not set (e.g. on Preview), mail goes to
// doych@doychzone.com, so tests never reach the card owner.
const FALLBACK_TO = 'doych@doychzone.com';

const senderAddress = () => {
  if (process.env.MARIA_CARD_FROM) return process.env.MARIA_CARD_FROM;
  const raw = process.env.SPEAKING_FROM || '';
  const m = raw.match(/<([^>]+)>/);
  const addr = m ? m[1] : (raw.includes('@') ? raw.trim() : 'onboarding@resend.dev');
  return 'Digital Card <' + addr + '>';
};

const clean = (v, max) => (v == null ? '' : String(v).trim().slice(0, max || 500));
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }
  let body = req.body || {};
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }

  // Honeypot: real visitors never fill the hidden "website" field.
  if (clean(body.website)) return res.status(200).json({ ok: true });

  const data = {
    name: clean(body.name, 200),
    email: clean(body.email, 200),
    phone: clean(body.phone, 60),
    note: clean(body.note, 3000),
  };
  if (!data.name) return res.status(400).json({ ok: false, error: 'Please add your name.' });
  if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    return res.status(400).json({ ok: false, error: 'Please check your email.' });
  }

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(500).json({ ok: false, error: 'Email service is not configured.' });

  const to = clean(process.env.MARIA_CARD_TO) || FALLBACK_TO;
  const subject = 'New contact from your card: ' + data.name.replace(/[\r\n]+/g, ' ');
  const rows = [['Name', data.name], ['Email', data.email], ['Phone', data.phone], ['Note', data.note]];
  const text = rows.map(([l, v]) => l + ': ' + (v || '(empty)')).join('\n') + '\n\nSent from doychzone.com/maria';
  const html = '<h2 style="font-family:sans-serif">' + esc(subject) + '</h2><table style="font-family:sans-serif;border-collapse:collapse">' +
    rows.map(([l, v]) => '<tr><td style="padding:4px 12px 4px 0;color:#666;vertical-align:top">' + l + '</td><td style="padding:4px 0;white-space:pre-wrap">' + esc(v || '(empty)') + '</td></tr>').join('') +
    '</table><p style="font-family:sans-serif;color:#999;font-size:12px">Sent from doychzone.com/maria</p>';

  const payload = { from: senderAddress(), to: [to], subject, text, html };
  if (data.email) payload.reply_to = data.email;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
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
