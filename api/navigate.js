export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    const { url } = req.body || {};
    if (!url || typeof url !== 'string') return res.status(400).json({ error: 'Missing url' });
    return res.status(200).json({ ok: true, action: 'navigate', url });
  } catch (e) {
    return res.status(500).json({ ok: false, error: String(e) });
  }
}
