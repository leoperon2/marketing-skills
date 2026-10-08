import {Composition} from 'remotion';
import {Stopper} from './Stopper';
import cfg from './layers.json';

export const Root: React.FC = () => (
  <Composition
    id="Stopper"
    component={Stopper}
    width={cfg.W}
    height={cfg.H}
    fps={cfg.FPS}
    durationInFrames={Math.round(cfg.T * cfg.FPS)}
  />
);
