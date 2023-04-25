#ライブラリのインポート
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

#dataframeから指定したラベルの列を抽出する
def choosename(df:pd.DataFrame,labels:[str]=["初投票回","charid"])->pd.DataFrame : 
    return pd.DataFrame([df[s] for s in labels]   ).T

#モデルのtemplate を展開するための関数
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
parser = argparse.ArgumentParser(description='touhou character vote analysis in stan.')
parser.add_argument("T",help="election times(number)",default=T,type=int)
parser.add_argument("TM",help="time delay of effect",default=TM,type=int)
parser.add_argument("suffix",help="suffix of model and result report",default="withindivisual")
args = parser.parse_args()

T=args.T
TM=args.TM

suffix=args.suffix

# 投票回数別キャラクター総数(決め打ち)
Nchar=[25,48,67,92,113,134,
      152,157,169,189,202,220,
      227,247,248,260,268,270]

# モデルのファイル名
template_fname="model/charpower_template_"+suffix+".stan"
model_fname="model/charpower_"+suffix+".stan"
renderfromfile(template_fname,model_fname,{'T':T,"T1":T+1,"TM":TM})
# モデルの読み込み
with open(model_fname) as f:
     model_code=f.read()

# 投票数の割合の読み込み
char_points_ratio=pd.read_csv("data/char_points_ratio.csv")
char_points_ratio=char_points_ratio[char_points_ratio.columns[2:]]
# 自機キャラ、ボスキャラ、非整数作品登場キャラの名前に対応したcharidの読み込み、モデル内でindexとして使われる
mainchartable=choosename(pd.read_csv("data/mainchar_integer_list.csv"),["初投票回","charid"])
bosschartable=choosename(pd.read_csv("data/bosslist.csv"),["初投票回","charid","bosslevel"])
subchardata=choosename(pd.read_csv("data/char_noninteger_list.csv"),["初登場回","charid"])
#秘封倶楽部、書籍キャラ、その他キャラの名前に対応したcharidの読み込み
hifuudata=choosename(pd.read_csv("data/hifuu_list.csv"),["charid"])
booksdata=choosename(pd.read_csv("data/bookchar_list.csv"),["charid"])
miscdata=choosename(pd.read_csv("data/misc_chars.csv"),["charid"])

#Tと投票回があっているかどうかの確認
assert(len(Nchar)==T)
assert(Nchar[-1]==len(char_points_ratio))

#投票数の割合char_points_ratioの非0の要素だけをとり、モデル計算の収束のためにごく小さな値を加える。　
cnn=char_points_ratio.to_numpy().T+1e-20
cn=[cnn[i,:Nchar[i]] for i in range(T)]

#numpyの整数フォーマットに変換する
bookchars=booksdata.to_numpy().astype("int64").T[0]
hifuuchars=hifuudata.to_numpy().astype("int64").T[0]
miscchars=miscdata.to_numpy().astype("int64").T[0]

#modelに入力するデータを辞書として定義する
data={
        "T":T,#num of elections
        "TM":TM,#time window size
        "Nchar":Nchar,
        "Ncharmax":max(Nchar),
        "Nmain":len(mainchartable),#  num. of integer main characters 
        "Nboss":len(bosschartable),#  num. of integer bosses
        "Nsub":len(subchardata),#  num. of noninteger characters 
        "Nbook":len(booksdata),
        "Nhifuu":len(hifuudata),
        "Nmisc":len(miscdata),

        "mainchars":mainchartable.to_numpy().astype("int64"),
        "bosschars":bosschartable.to_numpy().astype("int64"),
        "subchars":subchardata.to_numpy().astype("int64"),

        "bookchars":bookchars,
        "hifuuchars":hifuuchars,
        "miscchars":miscchars
}
# 異なる長さのchars_vote_normalをdataに追加
for i in range(T):
    data["chars_vote_normal"+str(i+1)]=cn[i]
    
#dataを代入するしてモデルをコンパイルする
buildmodel= stan.build(model_code, data=data, random_seed=4)
#事後分布のサンプリング計算の実行
fit = buildmodel.sample(num_chains=4, num_samples=2000) 

#実行結果の保存
with open('fit_'+suffix+'.pkl', 'wb') as w:
    pickle.dump(fit, w)
print("fin")

#実行結果全体の保存
fit.to_frame().to_csv("postdata/posterior_"+suffix+".csv") 
#サマリーの保存
summary = az.summary(fit)
summary.to_csv("postdata/summary_"+suffix+".csv") 

#グラフ描画、保存
visdata = az.from_pystan(posterior=fit)
#trace plot
az.plot_trace(visdata)
plt.savefig("img/posterior_charm_trace_"+suffix+".png")

#forest plot
az.plot_forest(visdata)
plt.savefig("img/posterior_charm_"+suffix+".png")

#maincharpowerだけのforest plot
az.plot_forest(visdata,var_names=("maincharpower"))
plt.savefig("img/posterior_charm_maincharpower"+suffix+".png")

#indivisualだけのforest plot
az.plot_forest(visdata,var_names=("indivisual"))
plt.savefig("img/posterior_charm_indivisual"+suffix+".png")

#indivisual 上位の平均、標準偏差の図保存
summary["名前"]=char_points_ratio["名前"].values
summary=summary.sort_values(by="mean")
summary=summary.filter(like='indivisual', axis=0)
px.bar(summary[-20:], y='名前', x='mean',orientation="h", width=800, height=800).savefig("img/char_indivisual_mean_20"+suffix+".png")
px.bar(summary[-20:], y='名前', x='sd',orientation="h", width=800, height=800).savefig("img/char_indivisual_sd_20"+suffix+".png")
#