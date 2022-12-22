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

  simplex [Nchar] chars_vote_normal[T];//normalized vote num. 1:rate
  int  mainchars[Nmain,2] ;//voteid(of int title), charid
  int  bosschars[Nboss,3] ;//voteid(of int title), charid(boss), bosslevel
    int subchars [Nsub,2];//voteid(of nonint title), charid

//  matrix<int=1>  [Nmusic][T] musics;
}
parameters {
  matrix <lower=0>[Ninttitle,TM] sigma;//coef of integer title main characters 
  matrix <lower=0>[Ninttitle,TM] b; //coef of integer title bosses
  matrix <lower=0>[Nnoninttitle,TM] s;// coef of noninteger title members
//  vector<real> eps[Nchar];  // indivisual charm

//  vector<real> nu[T];//total vote amount
}

//transformed parameters {
//}

model {
  for(t in 1:T){//election
    vector[Nchar] dth;
      for(i in 1:Nchar){
          matrix[Nmain,TM] mains;
          matrix[Nboss,TM] bosses;
          matrix[Nsub,TM] subs;

        //integer main chars
        for(j in 1:Nmain){
           if((i-1)==mainchars[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == mainchars[j][1]){//vote id
                    mains[j][l]=sigma[t][l];
                    print("hit sigma",i-1,",",l,"\n");
                }else{
                    mains[j][l]=0;
                }
              }
              //print("hit charid",i-1);
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
                if( t-l+1 == bosschars[j][1]){//vote id
                    bosses[j][l]=b[t][l]*bosschars[j][3];//bosslevel
                    print("hit boss charid",i-1," at ",t);
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
                    
        //noninteger(sub)chars
        for(j in 1:Nsub){
           if(i==subchars[j][2]){//char index
               for(l in 1:TM){
                if( t-l+1 == subchars[j][1]){
                    subs[j][l]=s[t][l];
                    print("hit nonint charid",i-1," at ",t);
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
        dth[i]=sum(mains)+sum(bosses)+sum(subs);///+eps[i];
        //print("sigma",sigma);
        //print("b",b);
        //print("s",s);
        //print("mains",mains);
        //print("bosses",bosses);        
        //print("subs",subs);        
        }
        
        print("----dth--",t,"-----",dth);       
        chars_vote_normal[t]~dirichlet(dth);
      }
}
  
