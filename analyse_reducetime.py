#https://pystan.readthedocs.io/en/latest/
import stan
import pandas as pd
import arviz as az
import matplotlib.pyplot as plt
import pickle

T=18

def choosename(df:pd.DataFrame,labels:[str]=["初投票回","charid"])->pd.DataFrame : 
    return pd.DataFrame([df[s] for s in labels]   ).T

model_fname="model/charpower_reducetime.stan"

with open(model_fname) as f:
     model_code=f.read()

char_points_ratio=pd.read_csv("data/char_points_ratio.csv")

#only for length
Ninttitle=len(pd.read_csv("data/integertitles.csv"))
Nnonintntitle=len(pd.read_csv("data/nonintegertitles.csv"))

#indexdata
mainchartable=choosename(pd.read_csv("data/mainchar_integer_list.csv"),["初投票回","charid"])
bosschartable=choosename(pd.read_csv("data/bosslist.csv"),["初投票回","charid","bosslevel"])
subchardata=choosename(pd.read_csv("data/char_noninteger_list.csv"),["初登場回","charid"])

#print(char_points_ratio.head())
char_points_ratio=char_points_ratio[char_points_ratio.columns[2:]]

print(Ninttitle)
print(Nnonintntitle)
print(char_points_ratio.to_numpy().shape)
print(mainchartable.to_numpy().shape)
print(bosschartable.to_numpy().shape)
print(subchardata.to_numpy().shape)


TM=5
Nchar=[25,48,67,92,113,134,
      152,157,169,189,202,220,
      227,247,248,260,268,270]

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
        "Ninttitle":Ninttitle,# num. of integer titles
        "Nnoninttitle":Nnonintntitle,# num. of non integer titles

        "Nmain":len(mainchartable),#  num. of integer main characters 
        "Nboss":len(bosschartable),#  num. of integer bosses
        "Nsub":len(subchardata),#  num. of noninteger characters 
    # normalized vote num. 0:vote,1:rate
        "chars_vote_normal1":cn[0],
        "chars_vote_normal2":cn[1],
        "chars_vote_normal3":cn[2],
        "chars_vote_normal4":cn[3],
        "chars_vote_normal5":cn[4],
        "chars_vote_normal6":cn[5],
        "chars_vote_normal7":cn[6],
        "chars_vote_normal8":cn[7],
        "chars_vote_normal9":cn[8],
        "chars_vote_normal10":cn[9],
        "chars_vote_normal11":cn[10],
        "chars_vote_normal12":cn[11],
        "chars_vote_normal13":cn[12],
        "chars_vote_normal14":cn[13],
        "chars_vote_normal15":cn[14],
        "chars_vote_normal16":cn[15],
        "chars_vote_normal17":cn[16],
        "chars_vote_normal18":cn[17],

        "mainchars":mainchartable.to_numpy().astype("int64"),
        "bosschars":bosschartable.to_numpy().astype("int64"),
        "subchars":subchardata.to_numpy().astype("int64")
}

posterior = stan.build(model_code, data=data, random_seed=3)
fit = posterior.sample(num_chains=4, num_samples=6000)

with open('fit_reducetime.pkl', 'wb') as w:
    pickle.dump(fit, w)
print("fin")

#parameters
#sigma= fit["sigma"]
#s= fit["s"]
#b= fit["b"]
#eps=fit["eps"]

#print(sigma.shape)
#print(s.shape)

post_dataframe = fit.to_frame() 
post_dataframe.to_csv("postdata/posterior_charm_reduce.csv")
az.plot_trace(fit)
plt.savefig("img/posterior_charm_reduce.png")