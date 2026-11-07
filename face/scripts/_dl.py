import urllib.request
u = "https://gitee.com/spacemit-robotics/model-zoo-vision/raw/main/applications/face_recognition/scripts/download_models.sh"
print(urllib.request.urlopen(u, timeout=20).read().decode())
