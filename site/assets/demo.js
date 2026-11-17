// Telemetry explorer over 16 simulated sensors (24 h, 15-minute interval), exported from
// scripts/simulate_sensors.py. Bounds come from analytics/quality.py, z-scores follow
// analytics/anomalies.py (per sensor and metric, sample standard deviation).
const $ = id => document.getElementById(id);
const data = await (await fetch('assets/sample.json')).json();
const t0 = Date.parse(data.start), step = data.intervalMinutes * 6e4;
const fmt = v => v === null || !Number.isFinite(v) ? '—' : Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(2);

function stats(vals) {
  if (!vals.length) return null;
  const n = vals.length, mean = vals.reduce((a, b) => a + b, 0) / n;
  const sd = n > 1 ? Math.sqrt(vals.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1)) : 0;
  return { n, mean, sd, min: Math.min(...vals), max: Math.max(...vals) };
}
function render() {
  const s = data.sensors.find(x => x.id === $('es-sensor').value), m = $('es-metric').value, z = +$('es-z').value;
  $('es-zv').textContent = z.toFixed(1);
  const pts = s.series[m].map((v, i) => ({ i, v })).filter(p => p.v !== null);
  const [lo, hi] = data.bounds[m] || [-Infinity, Infinity];
  const all = stats(pts.map(p => p.v)), ok = pts.filter(p => p.v >= lo && p.v <= hi), clean = stats(ok.map(p => p.v));
  pts.forEach(p => { p.z = all.sd ? (p.v - all.mean) / all.sd : 0; p.an = Math.abs(p.z) > z; p.oob = !(p.v >= lo && p.v <= hi); });
  const expected = s.series[m].length, uptime = Math.min(pts.length / Math.max(expected, 1), 1) * 100;
  const t = (v, l, c = '') => `<div class="kpi-tile ${c}"><div class="v">${v}</div><div class="l">${l}</div></div>`;
  $('es-tiles').innerHTML = t(pts.length, `readings · ${uptime.toFixed(1)}% of expected slots`) + t(pts.filter(p => p.an).length, `z-score anomalies (|z| > ${z.toFixed(1)})`, pts.some(p => p.an) ? 'warn' : '') +
    t(pts.filter(p => p.oob).length, 'outside plausible range', pts.some(p => p.oob) ? 'bad' : '') + t(`${lo}–${hi}`, `bounds for ${m}`);
  // chart: clip y to a readable window around the plausible data, mark clipped points at the edge
  const vis = ok.length ? ok.map(p => p.v) : pts.map(p => p.v);
  let y0 = Math.min(...vis), y1 = Math.max(...vis); const pad = (y1 - y0) * .25 || 1; y0 -= pad; y1 += pad;
  const W = 760, H = 240, L = 44, B = 22, x = i => L + i / (expected - 1) * (W - L - 8), y = v => 8 + (y1 - Math.min(Math.max(v, y0), y1)) / (y1 - y0) * (H - B - 8);
  let g = '';
  if (Number.isFinite(lo)) g += `<rect x="${L}" y="${y(Math.min(hi, y1))}" width="${W - L - 8}" height="${Math.max(0, y(Math.max(lo, y0)) - y(Math.min(hi, y1)))}" class="band"/>`;
  for (let k = 0; k <= 4; k++) { const v = y0 + (y1 - y0) * k / 4; g += `<text x="${L - 6}" y="${y(v) + 3}" class="ax" text-anchor="end">${fmt(v)}</text>`; }
  for (let h = 0; h < expected; h += 24) g += `<text x="${x(h)}" y="${H - 6}" class="ax" text-anchor="middle">${new Date(t0 + h * step).toISOString().slice(11, 16)}Z</text>`;
  g += `<polyline class="ln" points="${ok.map(p => `${x(p.i).toFixed(1)},${y(p.v).toFixed(1)}`).join(' ')}"/>`;
  g += pts.map(p => `<circle cx="${x(p.i).toFixed(1)}" cy="${y(p.v).toFixed(1)}" r="${p.oob ? 5 : p.an ? 4 : 1.8}" class="${p.oob ? 'oob' : p.an ? 'an' : 'pt'}"><title>${new Date(t0 + p.i * step).toISOString().slice(0, 16).replace('T', ' ')} · ${p.v} · z ${p.z.toFixed(2)}${p.oob ? ' · impossible: drawn at the chart edge' : ''}</title></circle>`).join('');
  const svg = $('es-svg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.innerHTML = g;
  const line = st => st ? `mean ${fmt(st.mean)} · min ${fmt(st.min)} · max ${fmt(st.max)} · n ${st.n}` : 'no plausible readings';
  $('es-raw').innerHTML = line(all); $('es-clean').innerHTML = line(clean) + (pts.length - ok.length ? ` · <span class="pill bad">${pts.length - ok.length} excluded</span>` : '');
}
$('es-sensor').innerHTML = data.sensors.map(s => `<option value="${s.id}">${s.id} · ${s.type.replace('_', ' ')} · ${s.location}</option>`).join('');
function metrics() { const s = data.sensors.find(x => x.id === $('es-sensor').value); const ms = Object.keys(s.series); const cur = $('es-metric').value;
  const bad = m => s.series[m].filter(v => v !== null && !(v >= (data.bounds[m] || [-Infinity])[0] && v <= (data.bounds[m] || [0, Infinity])[1])).length;
  $('es-metric').innerHTML = ms.map(m => `<option${m === cur ? ' selected' : ''}>${m}</option>`).join('');
  if (!ms.includes(cur)) $('es-metric').value = ms.slice().sort((a, b) => bad(b) - bad(a))[0]; }
$('es-sensor').addEventListener('change', () => { metrics(); render(); });
['es-metric', 'es-z'].forEach(id => $(id).addEventListener('input', render));
metrics(); render();
