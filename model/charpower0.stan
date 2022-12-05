//https://stats.biopapyrus.jp/bayesian-statistics/stan/stan-block.html
//https://statmodeling.hatenablog.com/entry/state-space-model-many-terms

data {
  int<lower=0> T;//num of elections
  int<lower=0> TM;//time window size
  int<lower=0> Nchar;//num. of characters 
//  int<lower=0> Nmusic;//num. of characters 
  
  int<lower=0> Ninttitle;//num. of integer titles
  int<lower=0> Nnoninttitle;//num. of noninteger titles
  int<lower=0> Nmain;// num. of integer main characters 
  int<lower=0> Nboss;// num. of integer bosses
  int<lower=0> Nsub;// num. of noninteger characters 

  matrix<int=1> [Nchar][2] chars_vote_normal;//normalized vote num. 0:vote,1:rate
  matrix<int=1> [Nmain][2] mainchars;//
  matrix<int=1> [Nboss][2] bosschars;
  matrix<int=1> [Nsub][2]  subchars;
//  matrix<int=1>  [Nmusic][T] musics;
}
parameters {
  matrix<real> sigma[Ninttitle][TM];//coef of integer title main characters 
  matrix<real> b[Ninttitle][TM]; //coef of integer title bosses
  matrix<real> s[Nnoninttitle][TM];// coef of noninteger title members
//  vector<real> nu[T];//total vote amount
}

//transformed parameters {
//}

model {
  for(t in 2:T){//election
  matrix <real> mains[Nmain][TM];
  matrix <real> bosses[Nboss][TM];
  matrix <real> subs[Nsub][TM];
      for(i in 1:Nchar){
        //integer main chars
        for(j in 1:Nmain){
           if(i==mainchars[j][2]){//char index
               for(l in 1:TM){
                if( t-l == mainchars[j][1]){
                    mains[j][l]=sigma[t][l];
                }else{
                    mains[j][l]=0;
                }
            }
            }else{
              for(l in 1:TM){
                mains[j][l]=0;
              }
            }
        }
        //bosses
        for(j in 1:Nboss){
           if(i==bosschars[j][2]){//char index
               for(l in 1:TM){
                if( t-l == bosschars[j][1]){
                    bosses[j][l]=b[t][l];
                }else{
                    bosses[j][l]=0;
                }
            }
            }else{
              for(l in 1:TM){
                bosses[j][l]=0;
              }
            }
            }
        }            
        //noninteger(sub)chars
        for(j in 1:Nsub){
           if(i==subchars[j][2]){//char index
               for(l in 1:TM){
                if( t-l == subchars[j][1]){
                    subs[j][l]=s[t][l];
                }else{
                    subs[j][l]=0;
                }
            }
            }else{
              for(l in 1:TM){
                subs[j][l]=0;
              }
            }
            }
        chars_vote_normal[i][t]~logistic(sum(mains)+sum(bosses)+sum(subs));
        //chars[i][t] ~ poisson(nu[t]*(sum(mains)+sum(bosses)+sum(subs) )); //cross term
        }            
      }
   
  
