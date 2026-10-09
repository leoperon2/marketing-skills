import asyncio, sys, subprocess, time
from pathlib import Path
from playwright.async_api import async_playwright
D=Path(__file__).parent; OUT=D/"frames"; OUT.mkdir(exist_ok=True)
FPS=30; DUR=15
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg=await b.new_page(viewport={"width":384,"height":1920},device_scale_factor=1)
        await pg.goto("http://127.0.0.1:8765/index.html",wait_until="networkidle")
        await pg.wait_for_function("window.ready===true"); await pg.wait_for_timeout(500)
        for i in range(FPS*DUR):
            await pg.evaluate("t=>setTime(t)",i/FPS)
            await pg.locator("#s").screenshot(path=str(OUT/f"f{i:04d}.png"))
        await b.close()
srv=subprocess.Popen([sys.executable,'-m','http.server','8765','--bind','127.0.0.1','--directory',str(D)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try: asyncio.run(main())
finally: srv.terminate()
subprocess.run(["ffmpeg","-y","-v","error","-framerate",str(FPS),"-i",str(OUT/"f%04d.png"),"-an","-c:v","libx264","-profile:v","high","-pix_fmt","yuv420p","-crf","16",str(D/"Stopper_Saches_V6_384x1920_15s.mp4")],check=True)
