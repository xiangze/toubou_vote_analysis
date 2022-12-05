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
- pixiv ranking illustration
- https://docs.google.com/spreadsheets/d/1YKpwyCOLRWiC9jucljunxS41i75zUYojI3qx1JnIpVI/edit?usp=sharing

### related articles
- https://booth.pm/ja/items/2025481
- https://hisayukihonbun.booth.pm/tems/760429
- https://www.pixiv.net/artworks/68538151

## method
Bayesian analysis by using pystan/pymc

architecture

![architecture](img/vote_analyse_arch.drawio.png)

made by https://app.diagrams.net/

## model
### basic models
#### power(charm) model
for normalized vote numbers

$$
normVote_{i,t} \sim invlogit(\sum_{l=0}^5 main_{j(i,t-l),t-l} \sigma_{j,l} \\ + \sum_{l=0}^5 boss_{j(i,t-1),t-l}Lv_i b_{j(i,t-l),l} 
\\ +\sum_{l=0}^5 sub_{j(i,t-l)} s_{j,l}
 )
$$
##### table flags (1 or 0)
$main_{j(i,t),t}$ i is main character of subtitle just before tth vote
$boss_{j(i,t),t}$ i is boss character of subtitle just before tth vote
$Lv_i$           boss level of character i
$sub_{j(i,t),t}$ i is character of noninteger subtitle just before tth vote  
##### parameters

##### index
- t index of time(vote )
- l index of realtive time
- i index of characters
- j index of mainchar,boss,subtitle table

#### subtitle(topic) model

##


