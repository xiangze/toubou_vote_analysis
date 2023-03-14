//https://stats.biopapyrus.jp/bayesian-statistics/stan/stan-block.html
//https://statmodeling.hatenablog.com/entry/state-space-model-many-terms

data {
  int<lower=0> T;//num of elections
  int<lower=0> TM;//time window size
  int<lower=0> Nchar[T];//num. of characters 
  int<lower=0> Ncharmax;//num. of characters 
//  int<lower=0> Nmusic;//num. of characters 
  
  int<lower=0> Ninttitle;//num. of integer titles
  int<lower=0> Nnoninttitle;//num. of noninteger titles
  int<lower=0> Nmain;// num. of integer main characters 
  int<lower=0> Nboss;// num. of integer bosses
  int<lower=0> Nsub;// num. of noninteger characters 

  //normalized vote num. 1:rate
  simplex [Nchar[1]] chars_vote_normal1;
  simplex [Nchar[2]] chars_vote_normal2;
  simplex [Nchar[3]] chars_vote_normal3;
  simplex [Nchar[4]] chars_vote_normal4;
  simplex [Nchar[5]] chars_vote_normal5;
  simplex [Nchar[6]] chars_vote_normal6;
  simplex [Nchar[7]] chars_vote_normal7;
  simplex [Nchar[8]] chars_vote_normal8;
  simplex [Nchar[9]] chars_vote_normal9;
  simplex [Nchar[10]] chars_vote_normal10;
  simplex [Nchar[11]] chars_vote_normal11;
  simplex [Nchar[12]] chars_vote_normal12;
  simplex [Nchar[13]] chars_vote_normal13;
  simplex [Nchar[14]] chars_vote_normal14;
  simplex [Nchar[15]] chars_vote_normal15;
  simplex [Nchar[16]] chars_vote_normal16;
  simplex [Nchar[17]] chars_vote_normal17;
  simplex [Nchar[18]] chars_vote_normal18;

  int  mainchars[Nmain,2] ;//voteid(of int title), charid
  int  bosschars[Nboss,3] ;//voteid(of int title), charid(boss), bosslevel
  int subchars [Nsub,2];//voteid(of nonint title), charid

//  matrix<int=1>  [Nmusic][T] musics;
}
parameters {
  matrix <lower=0>[T,TM] sigma;//coef of integer title main characters 
  matrix <lower=0>[T,TM] b; //coef of integer title bosses
  matrix <lower=0>[T,TM] s;// coef of noninteger title members
  vector <lower=0>[Ncharmax] eps;  // indivisual charm
//  vector<real> nu[T];//total vote amount
}

//transformed parameters {
//}

model {
   for(i in 1:Ncharmax){
    eps[i]~uniform(1e-6,1000);
  }

  for(t in 1:T){//election
      for(l in 1:TM){
        sigma[t,l]~uniform(1e-6,1000);
        b[t,l]~uniform(1e-6,1000);
        s[t,l]~uniform(1e-6,1000);
      }

  //for(t in 1:1){//election
    vector[Nchar[t]] dth;
      for(i in 1:Nchar[t]){
          matrix[Nmain,TM] mains;
          matrix[Nboss,TM] bosses;
          matrix[Nsub,TM] subs;

        //integer main chars
        for(j in 1:Nmain){
           if((i-1)==mainchars[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == mainchars[j][1]){//vote id
                    mains[j][l]=sigma[t][l];
                    //print("hit sigma",i-1,",",l,"\n");
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
                    //print("hit boss charid",i-1," at ",t);
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
                    //print("hit nonint charid",i-1," at ",t);
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
        dth[i]=sum(mains)+sum(bosses)+sum(subs)+eps[i];
        //dth[i]=eps[i];
        //print("sigma",sigma);
        //print("b",b);
        //print("s",s);
        //print("mains",mains);
        //print("bosses",bosses);        
        //print("subs",subs);        
        }

//        print("----dth--",t,"-----",dth);       
        if(t==1){
                chars_vote_normal1~dirichlet(dth);
        }else if (t==2) {
                chars_vote_normal2~dirichlet(dth);
        }else if (t==3) {
                chars_vote_normal3~dirichlet(dth);
        }else if (t==4) {
                chars_vote_normal4~dirichlet(dth);
        }else if (t==5) {
                chars_vote_normal5~dirichlet(dth);
        }else if (t==6) {
                chars_vote_normal6~dirichlet(dth);
        }else if (t==7) {
                chars_vote_normal7~dirichlet(dth);
        }else if (t==8) {
                chars_vote_normal8~dirichlet(dth);
        }else if (t==9) {
                chars_vote_normal9~dirichlet(dth);
        }else if (t==10) {
                chars_vote_normal10~dirichlet(dth);
        }else if (t==11) {
                chars_vote_normal11~dirichlet(dth);
        }else if (t==12) {
                chars_vote_normal12~dirichlet(dth);
        }else if (t==13) {
                chars_vote_normal13~dirichlet(dth);
        }else if (t==14) {
                chars_vote_normal14~dirichlet(dth);
        }else if (t==15) {
                chars_vote_normal15~dirichlet(dth);
        }else if (t==16) {
                chars_vote_normal16~dirichlet(dth);
        }else if (t==17) {
                chars_vote_normal17~dirichlet(dth);
        }else if (t==18) {
                chars_vote_normal18~dirichlet(dth);
        }else{
        }
      }
}
  
