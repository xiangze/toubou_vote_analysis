#https://pystan.readthedocs.io/en/latest/
import stan
import pandas as pd
import arviz as az
import plotly.express as px
import matplotlib.pyplot as plt
import pickle
import argparse

#モデルのtemplate用
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./', encoding='utf8'))

#template utils
def frender(fname:str,d:dict):
    templ = env.get_template(fname)
    return templ.render(d)

def fwrite(f,fname:str):
    with open(fname,"w") as fw:
        fw.write(f)

def renderfromfile(tempname:str,outfname:str,d:dict):
    fwrite(frender(tempname,d) ,outfname)

#入力引数(パラメーター)
#投票開催数
T=18
#新作の影響の持続期間
TM=5
#モデルのファイル名suffix
suffix="withtitle"

#入力引数T, TMの処理
parser = argparse.ArgumentParser(description='touhou misic vote analysis in stan.')
parser.add_argument("T",help="election times(number)",default=T,type=int)
parser.add_argument("TM",help="time delay of effect",default=TM,type=int)
parser.add_argument("suffix",help="suffix of model and result report",default="withindivisual")
args = parser.parse_args()

T=args.T
TM=args.TM

suffix=args.suffix

# モデルのファイル名
template_fname="model/music_template_"+suffix+".stan"
model_fname="model/music_"+suffix+".stan"
renderfromfile(template_fname,model_fname,{'T':T,"T1":T+1,"TM":TM})

# モデルの読み込み
with open(model_fname) as f:
     model_code=f.read()

#登場順にソートされた正規化楽曲投票結果+作品、登場ステージ、登場年の一覧
music_points_ratio_id=pd.read_csv("data/music_point_ratio_sort.csv").fillna(0)

#登場順にソートされた正規化楽曲投票結果の抽出
offset=3
ratio=music_points_ratio_id.T[offset:offset+T].to_numpy()

# 投票回数別楽曲総数の計算
Nmusic=[]
for n in range(T):
    for i in range(len(ratio[n])-1,0,-1):
        if(ratio[n][i]!=0):
            Nmusic.append(i+1)
            break

#Tと投票回があっているかどうかの確認
assert(len(Nmusic)==T)
assert(Nmusic[-1]==len(ratio.T))

#列をintにする関数
def toint(df:pd.DataFrame):
    return df.to_numpy().astype("int64")

#各種flagをcsvファイルから取り出しintにする関数
def toflag(s:str):
    return toint(music_points_ratio_id[s])

#整数作品、非整数作品のflag作成 以下のdataの要素
music_points_ratio_id["isinteger"]=pd.DataFrame((music_points_ratio_id["番号"]*10%10==0) &( music_points_ratio_id["番号"] !=0))

#modelに入力するデータを辞書として定義する
data={
        "T":T,#num of elections
        "TM":TM,#time window size
        "Nmusic":Nmusic,
        "Nmusicmax":max(Nmusic),
        "electionnum":toflag("人気投票"),
        "order":toflag("Number"),
        "isinteger":toflag("isinteger"),
        "isnoninteger":toint(music_points_ratio_id["番号"]*10%10!=0),
        "isbook":toflag("isbook"),
        "isCD":toflag("isCD"),
        "isseihou":toflag("isseihou"),
        "ishifuu":toflag("ishifuu"),
        "isold":toflag("isold"),
        "isother":toflag("isother"),
        "isoriginal":toflag("isoriginal"),
    }

#モデル計算の収束のためにごく小さな値を加える。　
cnn=ratio+1e-20
# 異なる長さのchars_vote_normalをdataに追加
cn=[cnn[i,:Nmusic[i]] for i in range(T)]
for i in range(T):
    data["vote_normal"+str(i+1)]=cn[i]
  
#dataを代入するしてモデルをコンパイルする  
buildmodel= stan.build(model_code, data=data, random_seed=4)
#事後分布のサンプリング計算の実行
fit = buildmodel.sample(num_chains=4, num_samples=2000)

#実行結果の保存
with open('fit_music_'+suffix+'.pkl', 'wb') as w:
    pickle.dump(fit, w)
print("fin")

#実行結果全体の保存
fit.to_frame().to_csv("postdata/music_posterior_"+suffix+".csv") 
#グラフ描画、保存
visdata = az.from_pystan(posterior=fit)

az.plot_forest(visdata)
plt.savefig("img/music_posterior_charm_"+suffix+".png")

