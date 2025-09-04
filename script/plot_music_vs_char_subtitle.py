import streamlit as st
import pandas as pd

import plotly.express as px
from colorspacious import cspace_converter

import matplotlib as mpl
import matplotlib.pyplot as plt  # これを呼ばないと matplotlib.font_manager にアクセスできない

#日本語対応
plt.rcParams['font.family'] = 'Noto Sans CJK JP'
import shutil
from pathlib import Path

config_dir = Path(mpl.get_configdir())
config_dir.mkdir(exist_ok=True, parents=True)
default_config_path = Path(mpl.__file__).parent / "mpl-data/matplotlibrc"
config_path = config_dir / "matplotlibrc"
shutil.copyfile(default_config_path, config_path)

pp=st.plotly_chart
pscatter=lambda df,x,y,**args:pp(px.scatter(df,x,y,args))
pscatter_z=lambda df,x,y,c,**args:pscatter_z(df,x,y,c,args)

w=st.write
#color map
cm = plt.get_cmap("Spectral")

################
w("# 東方Project人気投票集計")
w("data from https://toho-vote.info/result")
w("第1回~第18回の音楽部門、キャラクター(人妖)部門の得票比率を登場作品(サブタイトル)ごとに集計し,その相関関係を図示する。")

w("## 作品ごとに集計したキャラポイント比率")
music_char_tate=pd.read_csv('data/music_char_tate.csv')
#group化
df=music_char_tate.groupby(['title','回']).sum()
dfmax=music_char_tate.groupby(['title','回']).max()
df['titlenum']=dfmax['titlenum']
music_char_group=df.rename_axis(["title",'回']).reset_index()

df=music_char_group
df
w('作品ごとに集計したキャラポイント比率、音楽ポイント比率 円の大きさはキャラポイント比率')
pp(px.scatter(df, x="音楽ポイント比率",y="キャラポイント比率", 
           animation_frame="回",
#           animation_group="title",
           size="キャラポイント比率", 
           color="titlenum", 
           hover_name='title',
           text="title",
#           ,'曲名','charname']
#           log_x=True, 
           size_max=100, 
           range_x=[0,.6], range_y=[0,.6],
           height=800,
           color_continuous_scale='Inferno'
           )
)

w("## サブタイトル(作品)と楽曲の相関")
musictitlerate_vs_titlerate=pd.read_csv("data/music_vs_subtitle.csv")
w("作品ポイント比率 vs 音楽集計ポイント比率 色はタイトルごと")
pp(px.scatter(musictitlerate_vs_titlerate,
              x="作品ポイント比率",y="音楽集計ポイント比率",color="名前n",hover_data=['名前'],
              color_continuous_scale='Inferno'))
w("作品ポイント比率 vs 音楽集計ポイント比率 色は投票回ごと")
pp( px.scatter(musictitlerate_vs_titlerate,
                    x="作品ポイント比率",y="音楽集計ポイント比率",color="回n",hover_data=['回'],
                    color_continuous_scale='Inferno')
)
w("""
作品によって音楽の人気に違いが見られる。
非想天則、花映塚は相対的に音楽が人気(ゲーム性によるのか)、永夜抄は相対的に作品が人気
投票回による違いはあまりない
""")
musictitlerate_vs_titlerate

w("## サブタイトル(作品)とキャラクターの相関")
chartitlerate_vs_titlerate=pd.read_csv("data/char_vs_subtitle.csv")
pp(px.scatter(chartitlerate_vs_titlerate,
                    x="作品ポイント比率",y="キャラ集計ポイント比率",color="名前n",hover_data=['名前'],
                    color_continuous_scale='Inferno')
)
pp( px.scatter(chartitlerate_vs_titlerate,
                    x="作品ポイント比率",y="キャラ集計ポイント比率",color="回n",hover_data=['回'],
                    color_continuous_scale='Inferno')
        )
w(
    """大まかには作品ポイントとキャラポイントは相関している。再登場のみで初出キャラがいない(非整数)作品はキャラ集計ポイントがNa ここでは0に張り付いている。
    投票回による傾向の違いは見られずタイトルごとにクラスタ化している。分散を見ると面白いかもしれない。紅魔郷は大きい。
    紅魔郷の人気が突出している。主人公(霊夢、魔理沙)は旧作が初登場で人数が少ないので比率は少なく見えているので別途解析が必要""")
chartitlerate_vs_titlerate

w("## 音楽、キャラ相関")
w("作品音楽集計間、作品キャラ集計間で大まかな傾向、性質はわかるが、第1回〜第12回の相関も見れる")
chartitlerate_vs_musictitlerate=pd.read_csv("data/char_vs_music_bysubtitle.csv")

chartitlerate_vs_titlerate=chartitlerate_vs_musictitlerate.fillna(0)

w("音楽ポイント比率 vs キャラ集計ポイント比率 色は投票回ごと")
pp( px.scatter(chartitlerate_vs_musictitlerate,
                x="音楽集計ポイント比率",
                y="キャラ集計ポイント比率",
                color="回n",hover_data=['回'],
                color_continuous_scale='Inferno'))

w("音楽ポイント比率 vs キャラ集計ポイント比率 色は作品ごと")
pp(
px.scatter(chartitlerate_vs_musictitlerate,
                x="音楽集計ポイント比率",
                y="キャラ集計ポイント比率",
                color="名前n",hover_data=['名前'],
                color_continuous_scale='Inferno')
                )

w("お互いに存在しないものが多く軸に張り付いていて見づらい")

chartitlerate_vs_musictitlerate