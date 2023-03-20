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
def choosename(df:pd.DataFrame,labels:[str]=["初投票回","charid"])->pd.DataFrame : 
    return pd.DataFrame([df[s] for s in labels]   ).T

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

parser = argparse.ArgumentParser(description='touhou character vote analysis in stan.')
parser.add_argument("T",help="election times(number)",default=T,type=int)
parser.add_argument("TM",help="time delay of effect",default=TM,type=int)
parser.add_argument("suffix",help="suffix of model and result report",default="withindivisual")
args = parser.parse_args()

T=args.T
TM=args.TM

suffix=args.suffix

Nchar=[25,48,67,92,113,134,
      152,157,169,189,202,220,
      227,247,248,260,268,270]

template_fname="model/charpower_template_"+suffix+".stan"
model_fname="model/charpower_"+suffix+".stan"
renderfromfile(template_fname,model_fname,{'T':T,"T1":T+1,"TM":TM})

with open(model_fname) as f:
     model_code=f.read()

char_points_ratio=pd.read_csv("data/char_points_ratio.csv")
char_points_ratio=char_points_ratio[char_points_ratio.columns[2:]]
#indexdata
mainchartable=choosename(pd.read_csv("data/mainchar_integer_list.csv"),["初投票回","charid"])
bosschartable=choosename(pd.read_csv("data/bosslist.csv"),["初投票回","charid","bosslevel"])
subchardata=choosename(pd.read_csv("data/char_noninteger_list.csv"),["初登場回","charid"])

print(char_points_ratio.to_numpy().shape)
print(mainchartable.to_numpy().shape)
print(bosschartable.to_numpy().shape)
print(subchardata.to_numpy().shape)

assert(len(Nchar)==T)
assert(Nchar[-1]==len(char_points_ratio))
#print(mainchartable.to_numpy().astype("int64"))
#print(bosschartable.to_numpy().astype("int64"))
#print(subchardata.to_numpy())

cnn=char_points_ratio.to_numpy().T+1e-20
cn=[cnn[i,:Nchar[i]] for i in range(T)]

data={
        "T":T,#num of elections
        "TM":TM,#time window size
        "Nchar":Nchar,
        "Ncharmax":max(Nchar),
        "Nmain":len(mainchartable),#  num. of integer main characters 
        "Nboss":len(bosschartable),#  num. of integer bosses
        "Nsub":len(subchardata),#  num. of noninteger characters 
        "mainchars":mainchartable.to_numpy().astype("int64"),
        "bosschars":bosschartable.to_numpy().astype("int64"),
        "subchars":subchardata.to_numpy().astype("int64")
}
# normalized vote num. 0:vote,1:rate
for i in range(T):
    data["chars_vote_normal"+str(i+1)]=cn[i]
    
buildmodel= stan.build(model_code, data=data, random_seed=4)
fit = buildmodel.sample(num_chains=4, num_samples=6000) #,warmup=1000)

with open('fit_'+suffix+'.pkl', 'wb') as w:
    pickle.dump(fit, w)
print("fin")

#parameters
#sigma= fit["sigma"]
#s= fit["s"]
#b= fit["b"]
#eps=fit["eps"]

#print(sigma.shape)
#print(s.shape)

fit.to_frame().to_csv("postdata/posterior_"+suffix+".csv") 
visdata = az.from_pystan(posterior=fit)

az.plot_forest(visdata)
plt.savefig("img/posterior_charm_"+suffix+".png")

az.plot_forest(visdata,var_names=("maincharpower"))
plt.savefig("img/posterior_charm_maincharpower"+suffix+".png")
