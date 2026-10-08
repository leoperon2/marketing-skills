import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import cfg from './layers.json';

// Mesmo comportamento do animate_psd.py (posicoes, tempos e easings em layers.json).
const pulse = (t: number, t0: number, period: number, dur: number) => {
  if (t < t0) return 0;
  const u = (t - t0) % period;
  return u < dur ? Math.sin((Math.PI * u) / dur) : 0;
};
const clamp = (x: number) => Math.max(0, Math.min(1, x));
const outCubic = (t: number) => 1 - (1 - t) ** 3;
const outBack = (t: number, c = 1.70158) => { t -= 1; return 1 + (c + 1) * t ** 3 + c * t ** 2; };

type Anim = {start: number; dur: number; dx: number; dy: number; s0: number; ease: string};
const anim = cfg.anim as unknown as Record<string, Anim>;
const place = cfg.place as unknown as Record<string, number[]>;
const sizes = cfg.sizes as unknown as Record<string, number[]>;
const fade = new Set(cfg.fade);

export const Stopper: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / cfg.FPS;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {Array.from({length: 20}, (_, n) => {
        const [x, y, bs] = place[n];
        const [iw, ih] = sizes[n];
        const w = iw * bs, h = ih * bs;
        let s = 1, dx = 0, dy = 0, a = 1;
        const A = anim[n];
        if (A) {
          const k = (A.ease === 'back' ? outBack : outCubic)(clamp((t - A.start) / A.dur));
          dx = A.dx * (1 - k); dy = A.dy * (1 - k); s = A.s0 + (1 - A.s0) * k;
          a = fade.has(n) ? clamp((t - A.start) / (A.dur * 0.7)) : [1, 2, 3, 4].includes(n) ? clamp((t - A.start) / 0.2) : 1;
        }
        if (t > 1.4) {
          const ph = t * Math.PI;
          if (n === 3) dy += 5 * Math.sin(ph + 1);
          if (n === 4) dy += 5 * Math.sin(ph);
          if (n === 7) s *= 1 + 0.012 * Math.sin(ph);
          if (n === 7) s *= 1 + 0.05 * pulse(t, 4, 3, 0.7);
          if (n === 17) s *= 1 + 0.03 * Math.sin(ph * 1.5) + 0.08 * pulse(t, 5.5, 3, 0.7);
          if (n === 8) s *= 1 + 0.07 * pulse(t, 6, 4, 0.8);
        }
        if (n === 0) s = 1 + (0.05 * t) / cfg.T;
        if (a <= 0 || n === 9 || n === 10 || n === 14) return null;
        return (
          <Img
            key={n}
            src={staticFile(`layers/${String(n).padStart(2, '0')}.png`)}
            style={{
              position: 'absolute', left: x, top: y, width: w, height: h,
              opacity: a, transformOrigin: '50% 50%',
              transform: `translate(${dx}px, ${dy}px) scale(${s})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
