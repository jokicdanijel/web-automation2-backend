export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
  const { selector, attribute } = req.query || {};
  if (!selector) return res.status(400).json({ error: 'Missing selector' });
  // Platzhalter: gibt Demo-Daten zurück
  return res.status(200).json({
    ok: true,
    action: 'extract',
    selector,
    attribute: attribute || null,
    value: 'DEMO_VALUE'
  });
}
