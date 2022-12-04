//https://stats.biopapyrus.jp/bayesian-statistics/stan/stan-block.html
//https://statmodeling.hatenablog.com/entry/state-space-model-many-terms

data {
  int<lower=0> T;//num of votes
  int<lower=0> Nchar;//num. of characters 
//  int<lower=0> Nmusic;//num. of characters 
  int<lower=0> Ntitle;//num. of titles
  int<lower=0> Nmainchars;// num. of integer main characters 
  int<lower=0> Nbosses;// num. of integer bosses
  int<lower=0> Nsubchars;// num. of noninteger characters 

  matrix<int=1> [Nchar][T] chars_vote_normal;//normalized vote num.
  matrix<int=1> [Nmain][T] mainchars;
  matrix<int=1> [Nboss][T] bosschars;
  matrix<int=1> [Nsub][T]  subchars;
//  matrix<int=1>  [Nmusic][T] musics;
}
parameters {
  matrix<real> sigma[Ntitle][TM];//coef of integer main characters 
  matrix<real> b[TM][Ntitle]; //coef of integer bosses
  matrix<real> s[TM][Ntitle];// coef of noninteger(subtitle) members
//  vector<real> nu[T];//total vote amount
}

transformed parameters {
matrix <real> mains[Nchar][TM];
matrix <real> bosses[Nchar][TM];
matrix <real> subs[Nchar][TM];
}

model {
  for(t in 2:T){
      for(i in 1:Nchar){
        //integer main chars
        for(j in 1:Ntitle){
            if(i==mainchars[j][1]){
               for(l in 1:TM){
                    mains[j][l]=mainchars[j][2]*sigma[mainchars[j][2]][l];
                }else{
                    mains[j][l]=0;
                }
            }
        }
        //bosses
        for(j in 1:Ntitle){
        }

        //subchars
      }
      chars_vote_normal[i][t]~logistic(sum(mains)+sum(bosses)+sum(subs));
      //chars[i][t] ~ poisson(nu[t]*(sum(mains)+sum(bosses)+sum(subs) )); //cross term
  }
  }
}