import os, urllib.request, time
url = "https://archive.spacemit.com/spacemit-ai/model_zoo/vision/buffalo_l/w600k_r50.q.onnx"
dst = "models/w600k_r50.q.onnx"
if not os.path.exists(dst):
    t = time.time()
    urllib.request.urlretrieve(url, dst)
    print(f"downloaded {os.path.getsize(dst):,} bytes in {time.time()-t:.1f}s")
else:
    print("exists")
