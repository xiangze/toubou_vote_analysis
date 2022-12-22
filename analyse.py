#https://pystan.readthedocs.io/en/latest/
import stan
import pandas as pd

def choosename(df:pd.DataFrame,labels:[str]=["初投票回","charid"])->pd.DataFrame : 
    return pd.DataFrame([df[s] for s in labels]   ).T

model_fname="model/charpower0.stan"
#model_fname="model/void.stan"

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

print(char_points_ratio.to_numpy().shape)
print(mainchartable.to_numpy().shape)
print(bosschartable.to_numpy().shape)
print(subchardata.to_numpy().shape)

T=18
TM=5

#print(mainchartable.to_numpy().astype("int64"))
#print(bosschartable.to_numpy().astype("int64"))
print(subchardata.to_numpy())

data={
        "T":T,#num of elections
        "TM":TM,#time window size
        "Nchar":len(char_points_ratio),# num. of characters 
        "Ninttitle":Ninttitle,# num. of integer titles
        "Nnoninttitle":Nnonintntitle,# num. of non integer titles

        "Nmain":len(mainchartable),#  num. of integer main characters 
        "Nboss":len(bosschartable),#  num. of integer bosses
        "Nsub":len(subchardata),#  num. of noninteger characters 

        "chars_vote_normal":char_points_ratio.to_numpy().T,# normalized vote num. 0:vote,1:rate
        "mainchars":mainchartable.to_numpy().astype("int64"),
        "bosschars":bosschartable.to_numpy().astype("int64"),
        "subchars":subchardata.to_numpy().astype("int64")
}

posterior = stan.build(model_code, data=data)

fit = posterior.sample(num_chains=4, num_samples=1000)
print("fin")

#parameters
sigma= fit["sigma"]
s= fit["s"]
b= fit["b"]

print(sigma.shape)
print(s.shape)

post_dataframe = fit.to_frame() 

