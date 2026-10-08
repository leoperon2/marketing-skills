# Stopper Digital Assaí — animação a partir do PSD

Saída: `stopper_384x1920.mp4` (384x1920, 15 s, 30 fps, H.264, sem áudio).

Para rodar na sua máquina (Windows):

    pip install psd-tools scipy numpy pillow
    python animate_psd.py produtos.psd diferenciais.psd saida.mp4   # 2o PSD (diferenciais) e opcional

Requer ffmpeg no PATH. O PSD é 1080x1920; as camadas são reposicionadas num layout vertical 384x1920.
Ajustes de posição/tempo ficam nos dicionários `PLACE` e `A` no topo do script.
Atenção: a área útil de comunicação do desenho do Assaí ainda não foi aplicada.

## Visualizar no navegador (Remotion)

    cd remotion
    npm install
    npm run dev        # abre o Remotion Studio em http://localhost:3000 (composição "Stopper")
    npm run render        # grava em D:\_JOBS\Videos Stopper Digital Assai\_RENDER\stopper_384x1920.mp4
    npm run render:local  # grava em remotion/out/ (alternativa)

Posições e tempos ficam em `remotion/src/layers.json`; a animação em `remotion/src/Stopper.tsx`.
