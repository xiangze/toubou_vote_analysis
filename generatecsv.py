from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
import requests
import os
import glob
import csv

#"+"is for first vote
def get_tabledata(table):
    return [[t.string for t in tr.find_all("td")]+[t.string for t in tr.find_all("th")] for tr in table]
def get_tableheader(table):
    return [[t.string for t in tr.find_all("th")] for tr in table]  

def openhtml(ddir,filename_tr):
    filename=ddir+filename_tr+".html"
    # dirty hack for character code
    try:
        with open(filename,"r") as fp:
            htmltext=fp.read()
    except:
        try:
            with open(filename,"r",encoding='euc_jp') as fp:
                htmltext=fp.read()
        except:
            try:
                with open(filename,"r",encoding='CP932') as fp:
                    htmltext=fp.read()
            except:
                print("cannot read"+filename)
    return htmltext
    
def souptable2csv(table,writedown=False,filename_tr=""):
    table_header=table.find_all("th")
    table_contents=table.find_all("tr")
    outdata  =get_tabledata(table_contents)
    outheader=get_tableheader(table_header)
    try:
        outdata[0]=outheader[0]
    except:
        print(filename_tr)
        print(table_header)
        
    if(writedown):
        with open(ddir+filename_tr+".csv", 'w') as fpw:
            writer = csv.writer(fpw, lineterminator='\n')
            writer.writerows(outdata)

def converthtml2csv(filename_tr,writedown=False):
    htmltext=openhtml(ddir,filename_tr)
    soup = BeautifulSoup(htmltext, "html.parser")
    table=soup 
    souptable2csv(table,writedown,filename_tr)

N=18
ddir="data"
url="https://toho-vote.info/result"


if(not (os.path.exists(ddir) and os.path.isdir(ddir))):
    os.mkdir(ddir)

import glob
htmlfiles=glob.glob("data/*/*.html")

for f in htmlfiles:
    filename_tr=f[4:]
    filename_tr=filename_tr.split(".")[0]
    converthtml2csv(filename_tr)




