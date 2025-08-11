export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { selector, timeoutMs = 15000 } = req.body || {};
  if (!selector) return res.status(400).json({ error: 'Missing selector' });
  // Platzhalter: tut so, als hätten wir gewartet
  return res.status(200).json({ ok: true, action: 'wait', selector, timeoutMs });
}
