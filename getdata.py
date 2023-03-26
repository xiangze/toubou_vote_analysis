from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
import requests
import os

N=18
ddir="data"
url="https://toho-vote.info/result"

if(not (os.path.exists(ddir) and os.path.isdir(ddir))):
    os.mkdir(ddir)
    r=requests.get(url)
else:


for n in range(1,N):
    with open(ddir/str(n)) as f:
        page=f.read()
        =page