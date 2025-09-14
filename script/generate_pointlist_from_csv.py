import pandas as pd
import glob
from functools import reduce
import nayose
    
files_music=glob.glob("data/*/*音楽*.csv")
files_char=glob.glob("data/*/*人妖*.csv")+glob.glob("data/*/*キャラ*.csv")
files_title=glob.glob("data/*/*作品*.csv")

cols={
    "人妖":['順位', '前回', '前々', '名前', 'ポイント', '一押し', 'コメント', '支援作品', '　'],
    "人妖short":['順位', '名前', 'ポイント', 'Unnamed: 3', 'コメント'],
    "音楽":["順位","前回","前々","名前","ポイント","一推し","コメント"," "],
    "作品":["順位","前回","前々","名前","ポイント","一推し","コメント"," "]
    }

for k,files in {"音楽":files_music,"人妖":files_char,"作品":files_title}.items():
    dfs=[]
    for f in files:
        df=pd.read_csv(f)
        print(f,list(df.columns))
        df=df.rename(columns=lambda x: x.replace('曲名', '名前'))
        try:
            df["ポイント"]=df["ポイント"].str.replace(",","")
            df["ポイント"]=df["ポイント"].astype(int)
        except:
            pass

        N=int(f.split("/")[1])
        df=nayose.nayose(df,k,N=N)
        print("名寄せ後",list(df.columns))

        if(k=="人妖"):
            df=nayose.columnfunc_char(df,N)
        else:
            if(len(df.columns)==0):
                df.columns=cols[k]
            elif(not "名前"in df.columns or not "ポイント" in df.columns ):
                if(len(df.columns)<len(cols[k])):
                    df.columns=cols[k][:len(df.columns)]             
                elif(len(df.columns)>len(cols[k])):       
                    df.columns=cols[k]+[" "]*(len(df.columns)-len(cols[k]))
                else:
                    df.columns=cols[k]

        print(list(df.columns))


        df=df[["名前","ポイント"]]
        df.columns=["名前",f"{N}回目ポイント"]
        dfs.append(df)
    merged_df = reduce(lambda l, r: pd.merge(l, r, on="名前", how='outer'), dfs)
    merged_df.to_csv(f"data/{k}_points_merge.csv")

