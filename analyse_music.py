#https://pystan.readthedocs.io/en/latest/
import stan
import pandas as pd
import arviz as az
import matplotlib.pyplot as plt
import pickle
import argparse
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./', encoding='utf8'))

#for dataframe
#def choosename(df:pd.DataFrame,labels:[str]=["初投票回","charid"])->pd.DataFrame : 
#    return pd.DataFrame([df[s] for s in labels]   ).T

#template utils
def frender(fname:str,d:dict):
    templ = env.get_template(fname)
    return templ.render(d)

def fwrite(f,fname:str):
    with open(fname,"w") as fw:
        fw.write(f)

def renderfromfile(tempname:str,outfname:str,d:dict):
    fwrite(frender(tempname,d) ,outfname)

T=18
TM=5
suffix="withtitle"

parser = argparse.ArgumentParser(description='touhou misic vote analysis in stan.')
parser.add_argument("T",help="election times(number)",default=T,type=int)
parser.add_argument("TM",help="time delay of effect",default=TM,type=int)
parser.add_argument("suffix",help="suffix of model and result report",default="withindivisual")
args = parser.parse_args()

T=args.T
TM=args.TM

suffix=args.suffix

template_fname="model/music_template_"+suffix+".stan"
model_fname="model/music_"+suffix+".stan"
renderfromfile(template_fname,model_fname,{'T':T,"T1":T+1,"TM":TM})

with open(model_fname) as f:
     model_code=f.read()

music_points_ratio_id=pd.read_csv("data/music_point_ratio_re.csv").fillna(0)

offset=3
ratio      =music_points_ratio_id.T[offset:offset+T].to_numpy()

#print(music_points_ratio_id.shape)
print(ratio.shape)

Nmusic=[]
for n in range(T):
    for i in range(len(ratio[n])-1,0,-1):
        if(ratio[n][i]!=0):
            Nmusic.append(i+1)
            break

print(Nmusic)
assert(len(Nmusic)==T)
assert(Nmusic[-1]==len(ratio.T))

data={
        "T":T,#num of elections
        "TM":TM,#time window size
        "Nmusic":Nmusic,
        "Nmusicmax":max(Nmusic),

        "electionnum":music_points_ratio_id["人気投票"].to_numpy().astype("int64"),
        "isinteger":(music_points_ratio_id["番号"]*10%10==0).to_numpy().astype("int64"),
        "isnoninteger":(music_points_ratio_id["番号"]*10%10!=0).to_numpy().astype("int64"),
        "order":music_points_ratio_id["order"].to_numpy().astype("int64"),
        "isbook":music_points_ratio_id["書籍"].to_numpy().astype("int64"),
        "isCD":music_points_ratio_id["CD"].to_numpy().astype("int64"),
        "ishifuu":music_points_ratio_id["秘封"].to_numpy().astype("int64"),
    }

# normalized vote num. 0:vote,1:rate
cnn=ratio+1e-20
cn=[cnn[i,:Nmusic[i]] for i in range(T)]
for i in range(T):
    data["vote_normal"+str(i+1)]=cn[i]
    
buildmodel= stan.build(model_code, data=data, random_seed=4)
fit = buildmodel.sample(num_chains=4, num_samples=6000,warmup=1000)

with open('fit_'+suffix+'.pkl', 'wb') as w:
    pickle.dump(fit, w)
print("fin")

fit.to_frame().to_csv("postdata/posterior_"+suffix+".csv") 
visdata = az.from_pystan(posterior=fit)

az.plot_forest(visdata)
plt.savefig("img/posterior_charm_"+suffix+".png")

#az.plot_forest(visdata,var_names=("maincharpower"))
#plt.savefig("img/posterior_charm_"+suffix+".png")

