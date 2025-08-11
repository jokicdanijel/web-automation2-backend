export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { selector, text } = req.body || {};
  if (!selector || typeof text !== 'string') return res.status(400).json({ error: 'Missing selector or text' });
  return res.status(200).json({ ok: true, action: 'type', selector, textLength: text.length });
}
