// =========================================================
// Image-sequence player for scroll-scrubbed video.
// Frames are numbered JPGs (001.jpg, 002.jpg, ...). They load in
// passes (every 16th frame first, then filling the gaps), so
// scrubbing works almost immediately and gets smoother as more
// frames arrive.
// =========================================================
export function createSequence(base, count) {
  const imgs = new Array(count);
  const loaded = new Uint8Array(count);
  let started = false;

  function load() {
    if (started) return;
    started = true;
    const order = [];
    const seen = new Uint8Array(count);
    [16, 8, 4, 2, 1].forEach((step) => {
      for (let i = 0; i < count; i += step) {
        if (!seen[i]) {
          seen[i] = 1;
          order.push(i);
        }
      }
    });
    if (!seen[count - 1]) order.push(count - 1);
    let next = 0;
    let inflight = 0;
    const pump = () => {
      while (inflight < 6 && next < order.length) {
        const i = order[next++];
        const im = new Image();
        inflight++;
        im.decoding = 'async';
        im.onload = () => {
          loaded[i] = 1;
          inflight--;
          pump();
        };
        im.onerror = () => {
          inflight--;
          pump();
        };
        im.src = `${base}/${String(i + 1).padStart(3, '0')}.jpg`;
        imgs[i] = im;
      }
    };
    pump();
  }

  // closest frame that has finished loading
  function nearest(i) {
    for (let d = 0; d < count; d++) {
      if (i - d >= 0 && loaded[i - d]) return i - d;
      if (i + d < count && loaded[i + d]) return i + d;
    }
    return -1;
  }

  return { count, imgs, loaded, load, nearest };
}
