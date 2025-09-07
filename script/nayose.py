import pandas as pd

def cleantitle(df:pd.DataFrame,c:str="Track Name"):
    df[c]=df[c].replace('\u3000.*',"",regex=True)
    df[c]=df[c].replace('～.*',"",regex=True)
    df[c]=df[c].replace('〜.*',"",regex=True)
    df[c]=df[c].replace(' - .*',"",regex=True)
    df[c]=df[c].replace(' $',"",regex=True)
    df[c]=df[c].replace('　',"",regex=True)
    df[c]=df[c].replace('\(.*\)',"",regex=True)
    df[c]=df[c].replace('（.*）',"",regex=True)
    return df

def cleantouhou(df:pd.DataFrame,c:str="title"):
    df[c]=df[c].replace('^東方',"",regex=True)    
    return df

def remove_English_title(totaltable,c="名前"):
    totaltable[c]=totaltable[c].replace('\u3000.*',"",regex=True)
    totaltable[c]=totaltable[c].replace('～.*',"",regex=True)
    totaltable[c]=totaltable[c].replace(' - .*',"",regex=True)

def rename_fill_drop(df:pd.DataFrame,cn:str):
    d=df.rename(columns={cn+"_x":cn})
    d[cn]=d[cn].fillna(d[cn+"_y"])
    d=d.drop(cn+"_y",axis=1)
    return d
    
def stage_nayose(p:pd.DataFrame)-> pd.DataFrame:
    p["stage"]=p.index.values
    p=p.replace("ボス.*","ボステーマ",regex=True)
    p=p.replace("取材のテーマ.","取材のテーマ",regex=True)
    p=p.replace("魔界.*","魔界",regex=True)
    
    p=p.replace("vs.*","非想天則vs誰か",regex=True)
    p=p.replace("会話.*","会話",regex=True)
    p=p.replace(".*エンディングテーマ","エンディングテーマ",regex=True)
    p=p.replace("撮影曲.","撮影曲",regex=True)

    p=p.replace(".*未使用.*","未使用曲",regex=True)
    p=p.replace(".*１面テーマ","１面テーマ",regex=True)
    p=p.replace(".*２面テーマ","２面テーマ",regex=True)
    p=p.replace(".*３面テーマ","３面テーマ",regex=True)
    p=p.replace("3面ボステーマ","３面ボステーマ",regex=True)
    p=p.replace(".*６面テーマ","６面テーマ",regex=True)
    p=p.replace(".*６面.*ボステーマ","６面ボステーマ",regex=True)

    p=p.replace("１.*面ボステーマ","１面ボステーマ",regex=True)
    p=p.replace("１０面テーマ","１０面以上テーマ",regex=True)
    p=p.replace("１５面テーマ","１０面以上テーマ",regex=True)
    p=p.replace("１６～１９面テーマ","１０面以上テーマ",regex=True)
    
    p=p.replace("EXTRAのテーマ","EXTRAテーマ",regex=True)
    p=p.replace("EXTRAステージテーマ","EXTRAテーマ",regex=True)
    p=p.replace("PHANTASMステージテーマ","PHANTASMテーマ",regex=True)

    p=p.replace("EXTRAステージボステーマ","EXTRAボステーマ",regex=True)
    p=p.replace("EXTRAボステーマ","EXTRAボステーマ",regex=True)
    p=p.replace("PHANTASMステージボステーマ","PHANTASMボステーマ",regex=True)
    p=p.replace("エキストラボステーマ","EXTRAボステーマ",regex=True)
    p=p.replace("最終ボステーマ","最終面ボステーマ",regex=True)
    
    p=p.replace(".*地獄.*","地獄",regex=True)
    
    p=p.replace(".*エンディングテーマ","エンディングテーマ",regex=True)
    p=p.replace("エキストラステージテーマ","エキストラステージ",regex=True)

    p=p.replace("グッドエンド.*","グッドエンド",regex=True)
    p=p.replace("ゲームオーバーテーマ.*","ゲームオーバーテーマ",regex=True)
    p=p.replace("バッドエンド.*テーマ","ゲームオーバーテーマ",regex=True)

    p=p.replace("スタッフロール.*","スタッフロール",regex=True)
    p=p.replace("タイトル.*","タイトル",regex=True)
    p=p.replace("ネームレジスト.*","ネームレジスト",regex=True)
    p=p.replace(".*のテーマ","キャラ特定のテーマ",regex=True)
    p=p.replace("キャラ特定のテーマ.*","キャラ特定のテーマ",regex=True)
    return p

def music_nayose(df,c="名前"):
    df[c]=df[c].replace("サーカスレヴァリエ（機械サーカス","サーカスレヴァリエ")
    df[c]=df[c].replace("My Maid， Sweet Maid","My Maid Sweet Maid")
    df[c]=df[c].replace("My Maid，Sweet Maid","My Maid Sweet Maid")
    df[c]=df[c].replace("Maple Dream ...","Maple Dream...")
    df[c]=df[c].replace("ハーセルヴス","ハーセルヴズ")
    df[c]=df[c].replace("ヴアル魔法図書館","ヴワル魔法図書館")
    df[c]=df[c].replace("リーインカネーション","リーインカーネーション")
    df[c]=df[c].replace("リーインカーネイション","リーインカーネーション")
   
    df[c]=df[c].replace("落日に生える逆さ城","落日に映える逆さ城")
    df[c]=df[c].replace("光輝く天球儀","光り輝く天球儀")
    #同じ名前を合計
    df=df.groupby(c).apply(lambda x: x.sum()).drop(c,axis=1).reset_index()
    return df