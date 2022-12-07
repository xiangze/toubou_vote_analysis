#https://pystan.readthedocs.io/en/latest/
import stan
import pandas as pd

def choosename(df:pd.DataFrame) ->pd.DataFrame : 
    return pd.DataFrame([df['名前'],df['charid']]).T

model_fname="model/charpower0.stan"
with open(model_fname) as f:
     model_code=f.read()

char_points_ratio=pd.read_csv("data/char_points_ratio.csv")

integertitledata=pd.read_csv("data/integertitles.csv")
nonintegertitledata=pd.read_csv("data/nonintegertitles.csv")
#indexdata
mainchartable=choosename(pd.read_csv("data/mainchar_integer_list.csv"))
bosschartable=choosename(pd.read_csv("data/bosslist.csv"))
subchardata=choosename(pd.read_csv("data/char_noninteger_list.csv"))

T=18
TM=5

data={
        "T":T,#num of elections
        "TM":TM,#time window size
        "Nchar":len(char_points_ratio),# num. of characters 
        "Ninttitle":len(integertitledata),# num. of integer titles
        "Nnoninttitle":len(nonintegertitledata),# num. of integer titles

        "Nmain":len(mainchartable),#  num. of integer main characters 
        "Nboss":len(char_points_ratio),#  num. of integer bosses
        "Nsub":len(subchardata),#  num. of noninteger characters 

        "chars_vote_normal":char_points_ratio.to_numpy(),# normalized vote num. 0:vote,1:rate
        "mainchars":mainchartable.to_numpy(),
        "bosschars":bosschartable.to_numpy(),
        "subchars":subchardata.to_numpy()
}


posterior = stan.build(model_code, data=data)

fit = posterior.sample(num_chains=4, num_samples=1000)

#parameters
sigma= fit["sigma"]
s= fit["s"]
b= fit["b"]

print(sigma.shape)
print(s.shape)

post_dataframe = fit.to_frame() 

