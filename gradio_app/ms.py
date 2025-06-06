import os
import requests
import subprocess
import time
from tqdm import tqdm

def download(filename, url):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024
        with open(filename, "wb") as file, tqdm(
            desc=f"Downloading {filename} from '{url}'...",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)

    except Exception as e:
        print(f"Error: {e}, retrying...")
        time.sleep(10)
        download(filename, url)


apkname = "MuseScore.AppImage"
extra_dir = "squashfs-root"

if not os.path.exists(apkname):
    download(
        filename=apkname,
        url="https://master.dl.sourceforge.net/project/musescore-linux-mirror/MuseScore.AppImage?viasf=1",
    )
    
if not os.path.exists(extra_dir):
    subprocess.run(["chmod", "+x", f"./{apkname}"])
    subprocess.run([f"./{apkname}", "--appimage-extract"])

MSCORE = f"./{extra_dir}/AppRun"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
