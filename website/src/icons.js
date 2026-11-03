// =========================================================
// Pixel-art icons: one source used both for the 3D voxel
// icons (Three.js) and the small flat icons on the page.
// Each letter is a colour, "." is empty.
// =========================================================

export const PALETTE = {
  K: '#14121c', // outline
  W: '#f7f2ea', // white
  L: '#cfd3dc', // light grey
  M: '#6b7280', // mid grey
  S: '#ff9933', // saffron
  D: '#c2551a', // dark saffron
  Y: '#ffd23f', // yellow
  G: '#22c55e', // green
  g: '#15803d', // dark green
  B: '#3b82f6', // blue
  b: '#1e3a8a', // dark blue
  R: '#ef4444', // red
};

export const ICONS = {
  // "HI!" speech bubble
  bubble: [
    '..KKKKKKKKKK..',
    '.KWWWWWWWWWWK.',
    'KWWWWWWWWWWWWK',
    'KWWSWSWSSSWSWK',
    'KWWSWSWWSWWSWK',
    'KWWSSSWWSWWSWK',
    'KWWSWSWWSWWWWK',
    'KWWSWSWSSSWSWK',
    'KWWWWWWWWWWWWK',
    '.KWWWWWWWWWWK.',
    '..KWWKKKKKKK..',
    '..KWK.........',
    '..KK..........',
  ],
  // idea / mindset
  bulb: [
    '....KKKK....',
    '..KKYYYYKK..',
    '.KYYWWYYYYK.',
    '.KYWWYYYYYK.',
    'KYYWYYYYYYYK',
    'KYYYYYYYYYYK',
    'KYYYYYYYYYYK',
    '.KYYYYYYYYK.',
    '.KYYYYYYYYK.',
    '..KYYYYYYK..',
    '...KYYYYK...',
    '...KLLLLK...',
    '...KMMMMK...',
    '...KLLLLK...',
    '....KMMK....',
    '.....KK.....',
  ],
  // the channel: a screen with a play button
  monitor: [
    'KKKKKKKKKKKKKKKK',
    'KMMMMMMMMMMMMMMK',
    'KMggggggggggggMK',
    'KMggggWgggggggMK',
    'KMggggWWggggggMK',
    'KMggggWWWgggggMK',
    'KMggggWWWWggggMK',
    'KMggggWWWgggggMK',
    'KMggggWWggggggMK',
    'KMggggWgggggggMK',
    'KMMMMMMMMMMMMMMK',
    'KKKKKKKKKKKKKKKK',
    '......KMMK......',
    '....KKKKKKKK....',
  ],
  // creating videos
  camera: [
    '...KKKKK........',
    '..KMMMMMK.......',
    'KKKKKKKKKKKKKKKK',
    'KLLLLLLLLLLLLRLK',
    'KLLLLKKKKKLLLLLK',
    'KLLLKbbbbbKLLLLK',
    'KLLKbBWBbbbKLLLK',
    'KLLKbWBBBbbKLLLK',
    'KLLKbBBBBbbKLLLK',
    'KLLLKbbbbbKLLLLK',
    'KLLLLKKKKKLLLLLK',
    'KLLLLLLLLLLLLLLK',
    'KKKKKKKKKKKKKKKK',
  ],
  // "your mindset is the remote control of your life"
  remote: [
    '.KKKKKKKK.',
    'KMMMMMMMMK',
    'KMRRMMMMMK',
    'KMRRMMMMMK',
    'KMMMMMMMMK',
    'KMMMSSMMMK',
    'KMMSSSSMMK',
    'KMMMSSMMMK',
    'KMMMMMMMMK',
    'KMWWMMWWMK',
    'KMMMMMMMMK',
    'KMWWMMWWMK',
    'KMMMMMMMMK',
    'KMGGGGGGMK',
    'KMMMMMMMMK',
    '.KKKKKKKK.',
  ],
  // contact
  envelope: [
    'KKKKKKKKKKKKKKKK',
    'KKWWWWWWWWWWWWKK',
    'KWKWWWWWWWWWWKWK',
    'KWWKWWWWWWWWKWWK',
    'KWWWKWWWWWWKWWWK',
    'KWWWWKWWWWKWWWWK',
    'KWWWWWKSSKWWWWWK',
    'KWWWWWWSSWWWWWWK',
    'KWWWWWWWWWWWWWWK',
    'KWWWWWWWWWWWWWWK',
    'KKKKKKKKKKKKKKKK',
  ],
  // kalash: the pot of amrit (nectar) from the churning of the ocean
  kalash: [
    '......DD......',
    '.....DSSD.....',
    '....DSSSSD....',
    '.GG..DSSD..GG.',
    'GgGGKKKKKKGGgG',
    '....KYYYYK....',
    '...KSSSSSSK...',
    '..KSSSSSSSSK..',
    '.KSYYYYYYYYSK.',
    'KSSSSSSSSSSSSK',
    'KSWSSSSSSSSSSK',
    'KSSSRRSSRRSSSK',
    '.KSSSSSSSSSSK.',
    '..KSSSSSSSSK..',
    '...KKKKKKKK...',
    '..KYYYYYYYYK..',
    '..KKKKKKKKKK..',
  ],
  heart: [
    '.KK...KK.',
    'KRRK.KRRK',
    'KRWRRRRRK',
    'KRRRRRRRK',
    '.KRRRRRK.',
    '..KRRRK..',
    '...KRK...',
    '....K....',
  ],
  star: [
    '....K....',
    '...KYK...',
    'KKKKYKKKK',
    'KYYYYYYYK',
    '.KYYYYYK.',
    '..KYYYK..',
    '.KYYKYYK.',
    '.KYK.KYK.',
    '.KK...KK.',
  ],
  flame: [
    '...K....',
    '..KSK...',
    '..KSSK..',
    '.KSSSK..',
    '.KSYSSK.',
    'KSSYYSSK',
    'KSYYWYSK',
    'KSYWWYSK',
    '.KSYYSK.',
    '..KKKK..',
  ],
  scissors: [
    'L.........L',
    'KL.......LK',
    '.KL.....LK.',
    '..KL...LK..',
    '...KL.LK...',
    '....KMK....',
    '...KRKRK...',
    '..KRK.KRK..',
    '.RRRR.RRRR.',
    'RR..R.R..RR',
    'RR..R.R..RR',
    '.RRRR.RRRR.',
  ],
};

/** List of { x, y, color } for every filled pixel, centred on 0,0 (y up). */
export function iconPixels(name) {
  const rows = ICONS[name];
  const h = rows.length;
  const w = Math.max(...rows.map((r) => r.length));
  const out = [];
  rows.forEach((row, y) => {
    [...row].forEach((ch, x) => {
      if (ch === '.' || !PALETTE[ch]) return;
      out.push({ x: x - (w - 1) / 2, y: (h - 1) / 2 - y, color: PALETTE[ch] });
    });
  });
  return out;
}

/** Draw an icon onto a <canvas> with a chunky extruded "voxel" shadow. */
export function drawIcon(canvas, name, scale = 4) {
  const rows = ICONS[name];
  if (!rows) return;
  const h = rows.length;
  const w = Math.max(...rows.map((r) => r.length));
  const depth = Math.max(1, Math.round(scale * 0.6));
  canvas.width = w * scale + depth;
  canvas.height = h * scale + depth;
  const g = canvas.getContext('2d');
  g.imageSmoothingEnabled = false;
  // extrusion
  g.fillStyle = 'rgba(0,0,0,0.55)';
  rows.forEach((row, y) =>
    [...row].forEach((ch, x) => {
      if (ch !== '.') g.fillRect(x * scale + depth, y * scale + depth, scale, scale);
    })
  );
  rows.forEach((row, y) =>
    [...row].forEach((ch, x) => {
      if (ch === '.' || !PALETTE[ch]) return;
      g.fillStyle = PALETTE[ch];
      g.fillRect(x * scale, y * scale, scale, scale);
    })
  );
}
