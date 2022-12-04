#https://pystan.readthedocs.io/en/latest/
import stan
import pandas as pd

def analyse(fname:str):
    with open(fname) as f:
        model_code=f.read()

chardata=pd.read_csv("data/charlist.csv")
titledata=pd.read_csv("data/title_.pointscsv")
mainchartable=pd.read_csv("data/main.csv")
#indexdata

data={"Nchar":len(chardata),"Ntitle"=len(title)}                             
posterior = stan.build(model_code, data=data)

fit = posterior.sample(num_chains=4, num_samples=1000)

sigma= fit["sigma"]
s= fit["s"]
s= fit[""]
print(sigma.shape)
print(s.shape)

post_dataframe = fit.to_frame() 

