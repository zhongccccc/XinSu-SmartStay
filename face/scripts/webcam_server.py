"""浏览器抓图 + 本地比对的小服务。

为什么要有它：这台机器上的物理摄像头只注册了 Media Foundation，
当前 OpenCV 5.0 的 MSMF 后端打不开，DirectShow 里又只有虚拟摄像头。
Chrome 走的是另一套采集路径，所以用浏览器取帧最省事，不用装驱动、不用降级 OpenCV。

    python scripts/webcam_server.py --id "E:\\人脸配对\\原.png" --port 8777

然后浏览器打开 http://127.0.0.1:8777 ，点「拍照比对」。
抓到的图存在 samples/webcam_live.jpg，结果同时写 samples/webcam_result.json。
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.config import Config  # noqa: E402
from facekit.io_utils import imread_unicode, imwrite_unicode  # noqa: E402
from facekit.pipeline import FaceVerifier  # noqa: E402

PAGE = """<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<title>身份证照 vs 摄像头 · 人脸比对</title>
<style>
  body{margin:0;background:#0f1115;color:#e6e6e6;font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
  .wrap{max-width:960px;margin:24px auto;padding:0 16px}
  h1{font-size:18px;font-weight:600;margin:0 0 4px}
  .sub{color:#8b93a1;font-size:12px;margin-bottom:16px}
  .stage{position:relative;background:#000;border-radius:10px;overflow:hidden;aspect-ratio:16/9}
  video,img#shot{width:100%;height:100%;object-fit:cover;display:block}
  img#shot{display:none}
  .count{position:absolute;inset:0;display:none;align-items:center;justify-content:center;
         font-size:120px;font-weight:200;color:#fff;text-shadow:0 2px 20px #000}
  .bar{display:flex;gap:10px;margin:14px 0}
  button{flex:1;padding:12px;border-radius:8px;border:0;font-size:15px;cursor:pointer;
         background:#2f6fed;color:#fff}
  button.ghost{background:#242833;color:#c9d1d9}
  button:disabled{opacity:.5;cursor:default}
  .result{display:none;margin-top:16px;padding:16px;border-radius:10px;background:#171a21;border:1px solid #242833}
  .verdict{font-size:26px;font-weight:700;margin-bottom:6px}
  .pass{color:#3fb950}.review{color:#d29922}.retry{color:#f85149}
  table{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}
  td{padding:4px 0;color:#8b93a1}td:last-child{text-align:right;color:#e6e6e6}
  .hint{color:#8b93a1;font-size:12px;margin-top:10px}
</style></head>
<body><div class="wrap">
  <h1>身份证照 vs 摄像头 · 1:1 人脸比对</h1>
  <div class="sub">坐正、正对镜头、距离 40~60 cm、让脸占画面 1/3 左右</div>
  <div class="stage">
    <video id="video" autoplay playsinline muted></video>
    <img id="shot" alt="capture">
    <div class="count" id="count"></div>
  </div>
  <div class="bar">
    <button id="btn">拍照比对</button>
    <button id="again" class="ghost" disabled>重拍</button>
  </div>
  <div class="result" id="result">
    <div class="verdict" id="verdict"></div>
    <div id="reason" class="sub" style="margin:0"></div>
    <table id="metrics"></table>
  </div>
  <div class="hint">只在本机处理，图片不离开这台电脑。</div>
</div>
<script>
let stream=null, busy=false;
const video=document.getElementById('video'), shot=document.getElementById('shot');
const btn=document.getElementById('btn'), again=document.getElementById('again');
const count=document.getElementById('count');

async function boot(){
  try{
    stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720},facingMode:'user'},audio:false});
    video.srcObject=stream;
  }catch(e){
    document.querySelector('.sub').textContent='无法打开摄像头：'+e.message;
    btn.disabled=true;
  }
}

function beep(freq,ms){
  try{
    const ctx=new (window.AudioContext||window.webkitAudioContext)();
    const o=ctx.createOscillator(), g=ctx.createGain();
    o.frequency.value=freq; o.connect(g); g.connect(ctx.destination);
    g.gain.value=0.05; o.start(); setTimeout(()=>{o.stop();ctx.close();},ms);
  }catch(e){}
}

async function capture(){
  if(busy) return; busy=true;
  btn.disabled=true;
  video.style.display='block'; shot.style.display='none';
  count.style.display='flex';
  for(let i=3;i>0;i--){ count.textContent=i; beep(880,80); await new Promise(r=>setTimeout(r,700)); }
  count.textContent=''; count.style.display='none'; beep(1320,120);

  const w=video.videoWidth||1280, h=video.videoHeight||720;
  const c=document.createElement('canvas'); c.width=w; c.height=h;
  c.getContext('2d').drawImage(video,0,0,w,h);
  const data=c.toDataURL('image/jpeg',0.92);

  shot.src=data; shot.style.display='block'; video.style.display='none';

  const res=await fetch('/shot',{method:'POST',headers:{'Content-Type':'application/json'},
                                body:JSON.stringify({image:data})});
  const r=await res.json();
  render(r);
  busy=false; again.disabled=false;
}

function render(r){
  const box=document.getElementById('result');
  box.style.display='block';
  const v=document.getElementById('verdict');
  const label={pass:'通过',review:'转人工复核',retry:'重拍'}[r.decision]||r.decision;
  v.className='verdict '+(r.decision||'');
  v.textContent=label+'   '+(r.score==null?'':r.score.toFixed(3));
  document.getElementById('reason').textContent=r.reason||'';
  const rows=[['阈值','high '+r.t_high+' / low '+r.t_low]];
  if(r.quality){
    rows.push(['人脸宽度',r.quality.face_px+' px']);
    rows.push(['清晰度',r.quality.blur]);
    rows.push(['亮度',r.quality.brightness]);
    rows.push(['侧脸 yaw',r.quality.yaw]);
    rows.push(['抬头/低头 pitch',r.quality.pitch]);
    if(r.quality.reasons&&r.quality.reasons.length) rows.push(['问题',r.quality.reasons.join('、')]);
  }
  if(r.latency_ms) rows.push(['耗时',r.latency_ms+' ms']);
  document.getElementById('metrics').innerHTML=rows.map(([k,v])=>`<tr><td>${k}</td><td>${v}</td></tr>`).join('');
}

function reset(){
  shot.style.display='none'; video.style.display='block';
  document.getElementById('result').style.display='none';
  again.disabled=true; btn.disabled=false;
}

btn.onclick=capture; again.onclick=reset;
boot();
</script></body></html>
"""

RESULT_PATH = Path("samples/webcam_result.json")
SHOT_PATH = Path("samples/webcam_live.jpg")


def make_handler(verifier: FaceVerifier, id_img: np.ndarray):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # 安静一点
            pass

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                body = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path != "/shot":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length))
                data = payload["image"].split(",", 1)[1]
                buf = np.frombuffer(base64.b64decode(data), np.uint8)
                frame = cv2.imdecode(buf, cv2.IMREAD_COLOR)
                if frame is None:
                    raise ValueError("图片解码失败")

                t0 = time.perf_counter()
                res = verifier.verify(id_img, [frame])
                elapsed = (time.perf_counter() - t0) * 1000

                SHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
                imwrite_unicode(str(SHOT_PATH), frame)

                f = res.frames[0]
                out = {
                    "decision": res.decision,
                    "score": res.score,
                    "reason": res.reason,
                    "t_high": res.detail.t_high if res.detail else None,
                    "t_low": res.detail.t_low if res.detail else None,
                    "quality": f.quality.as_dict() if f.quality else None,
                    "error": f.error,
                    "latency_ms": round(elapsed, 1),
                }
                RESULT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[shot] decision={res.decision} score={res.score:.3f} "
                      f"err={f.error} {elapsed:.0f}ms", flush=True)

                body = json.dumps(out, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:  # noqa: BLE001
                body = json.dumps({"decision": "retry", "reason": str(exc)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--id", required=True, help="身份证照路径")
    ap.add_argument("--port", type=int, default=8777)
    args = ap.parse_args()

    cfg = Config.load(args.config)
    cfg.match.min_valid_frames = 1  # 单帧抓拍
    verifier = FaceVerifier(cfg)
    id_img = imread_unicode(args.id)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(verifier, id_img))
    print(f"open http://127.0.0.1:{args.port}  (id={args.id})", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
