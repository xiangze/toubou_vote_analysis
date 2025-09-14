# Touhou Vote Analysis 

東方プロジェクト人気投票の解析

Bayesian analysis of Touhou project vote data

## data source
- https://toho-vote.info/result
- https://toho-vote.info/results

China(optional)
- https://touhou.vote/nav/ 
- https://touhou.vote/v10/?result=true 

### related information
- http://thwiki.info/?%BD%D0%B1%E9%A5%EA%A5%B9%A5%C8 title & charactors
- http://thwiki.info/?%A5%AD%A5%E3%A5%E9%CA%CC%A5%B9%A5%DA%A5%EB%A5%AB%A1%BC%A5%C9%2F1#v5aac3bf spell cards &charactors
- https://touhou.arrangement-chronicle.com/statistics music
- https://w.atwiki.jp/toho/pages/842.html#id_713b4b9a title & music & charactors

### pixiv
- [東方project人気投票](https://dic.pixiv.net/a/%E6%9D%B1%E6%96%B9project%E4%BA%BA%E6%B0%97%E6%8A%95%E7%A5%A8)
- [東方楽曲](https://dic.pixiv.net/a/%E6%9D%B1%E6%96%B9%E6%A5%BD%E6%9B%B2)
- [東方Projectの登場人物](https://dic.pixiv.net/a/%E6%9D%B1%E6%96%B9Project%E3%81%AE%E7%99%BB%E5%A0%B4%E4%BA%BA%E7%89%A9)

- pixiv ranking illustration
- https://docs.google.com/spreadsheets/d/1YKpwyCOLRWiC9jucljunxS41i75zUYojI3qx1JnIpVI/edit?usp=sharing

### related articles
- https://booth.pm/ja/items/2025481
- https://hisayukihonbun.booth.pm/tems/760429
- https://www.pixiv.net/artworks/68538151
- https://docs.google.com/spreadsheets/d/1NbdTXrPqA3df5wS37emN3RMFDH9Re2nApleYTlGKsp8/edit#gid=753814927

## method
### summary of elections
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
    https://colab.research.google.com/github/xiangze/touhou_vote_analysis/blob/main/summary.ipynb) 

### scraping
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
    https://colab.research.google.com/github/xiangze/touhou_vote_analysis/blob/main/download_and_scrape.ipynb)
### EDA
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/xiangze/toubou_vote_analysis/blob/main/EDA.ipynb)

### correcation between title/character/music ranking
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/xiangze/toubou_vote_analysis/blob/main/character_music_correlation.ipynb)

### relation between stages and votes
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/xiangze/toubou_vote_analysis/blob/main/stagewise.ipynb)

### bayesian analysis

run
```
 python analysis_char.py 18 18 sum
```
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/xiangze/toubou_vote_analysis/blob/main/stan_analyse.ipynb)


Bayesian analysis by using pystan/gensim

```
python3 analysis.py 18 5 modelsuffix
```
18 is election number, 5 is duration of time effect


<!--
architecture
![architecture](img/vote_analyse_arch.drawio.png)
made by https://app.diagrams.net/
-->

## model
### basic models
#### power(charm) model
for normalized vote numbers

$$
normVote_{i,t} \sim Dir(\sum_{l=1}^{TM} main_{j(i,t-l),t-l} \sigma_{j,l} \\ + \sum_{l=1}^{TM} boss_{j(i,t-1),t-l}Lv_i b_{j(i,t-l),l} 
\\ +\sum_{l=1}^{TM} sub_{j(i,t-l)} s_{j,l}+\epsilon_i
 )
$$

##### table flags (1 or 0)
- $main_{j(i,t),t}$ i is main character of subtitle just before tth election
- $boss_{j(i,t),t}$ i is boss character of subtitle just before tth election
- $Lv_i$           boss level of character i
- $sub_{j(i,t),t}$ i is character of noninteger subtitle just before tth election
##### parameters
- $\sigma$ coef of integer title main characters 
- b coef of integer title bosses
- s coef of noninteger title members
- $\epsilon_i$ indivisual term
##### index
- t index of time(election)
- l index of realtive time
- i index of characters
- j index of mainchar,boss,subtitle table

#### subtitle model(topic model)

$\theta_m \sim Dir(\alpha)$ K dimension

$\phi_m \sim Dir(\beta)$ V dimension

$z_n \sim Cat(\theta_m)$  K dimension

$w_n \sim Cat(\phi_{z_n})$ V dimension

- V num. of characters
- K num. of titles
- N num. of total votes
- M num. of elections
- $\alpha, \beta$ hyperparameter 

caluculate by using gemsim
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/xiangze/toubou_vote_analysis/blob/main/topicmodel.ipynb)

## Visualize result posterior distribution of parameters

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/xiangze/toubou_vote_analysis/blob/main/stan_analysis.ipynb)

## Reference
- https://mc-stan.org/docs/stan-users-guide/index.html
- https://statmodeling.hatenablog.com/entry/topic-model-4
- https://radimrehurek.com/gensim/
- https://atmarkit.itmedia.co.jp/ait/articles/1905/22/news007.html
