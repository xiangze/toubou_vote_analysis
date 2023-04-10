//https://stats.biopapyrus.jp/bayesian-statistics/stan/stan-block.html
//https://statmodeling.hatenablog.com/entry/state-space-model-many-terms

data {
  int<lower=0> T;//num of elections
  int<lower=0> TM;//time window size
  int<lower=0> Nchar[T];//num. of characters 
  int<lower=0> Ncharmax;//num. of characters 
//  int<lower=0> Nmusic;//num. of characters 
  int<lower=0> Nmain;// num. of integer main characters 
  int<lower=0> Nboss;// num. of integer bosses
  int<lower=0> Nsub;// num. of noninteger characters 

  //normalized vote num. 1:rate
  {% for t in range(1,T1) %}
  simplex [Nchar[{{t}}]] chars_vote_normal{{t}};  
  {%- endfor %}                

  int  mainchars[Nmain,2] ;//voteid(of int title), charid
  int  bosschars[Nboss,3] ;//voteid(of int title), charid(boss), bosslevel
  int subchars [Nsub,2];//voteid(of nonint title), charid

//  matrix<int=1>  [Nmusic][T] musics;
}
parameters {
  matrix <lower=0>[T,TM] maincharpower;//coef of integer title main characters 
  matrix <lower=0>[T,TM] bosspower; //coef of integer title bosses
  matrix <lower=0>[T,TM] subpower;// coef of noninteger title members
  vector <lower=0>[Ncharmax] indivisual;  // indivisual charm

  real <lower=0> mu_i,mu_m,mu_b,mu_s;
  real <lower=0> sigma_i,sigma_m,sigma_b,sigma_s;
}

//transformed parameters {
//}

model {
  mu_i~exponential(50);
  mu_m~exponential(100);
  mu_b~exponential(100);
  mu_s~exponential(100);;

  simga_i~student_t(4,0,100);
  sigma_m~student_t(4,0,100);
  sigma_b~student_t(4,0,100);
  sigma_s~student_t(4,0,100);

   for(i in 1:Ncharmax){
    indivisual[i]~normal(mu_i,sigma_i);//uniform(1e-6,1000);
  }

  for(t in 1:T){//election

      for(l in 1:TM){
        maincharpower[t,l]~normal(mu_m,sigma_m);//uniform(1e-6,1000);
        bosspower[t,l]~normal(mu_b,sigma_b);//uniform(1e-6,1000);
        subpower[t,l]~normal(mu_s,sigma_s);//uniform(1e-6,1000);
      }

      vector[Nchar[t]] dth;
  
      for(i in 1:Nchar[t]){//indivisual character
          matrix[Nmain,TM] mains;
          matrix[Nboss,TM] bosses;
          matrix[Nsub,TM] subs;

        //integer main chars
        for(j in 1:Nmain){
           if((i-1)==mainchars[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == mainchars[j][1]){//vote id
                    mains[j][l]=maincharpower[t][l];
                    //print("hit maincharpower",i-1,",",l,"\n");
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
           if(i==bosschars[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == bosschars[j][1]){//election id 
                    bosses[j][l]=bosspower[t][l]*bosschars[j][3];//bosslevel
                    //print("hit boss charid",i-1," at ",t);
                }else{
                    bosses[j][l]=0;
                }
              }

//              if(t==bosschars[j][1]){//title charm time independent
//                title[i]=titlepow[t];
//              }

            }else{
              for(l in 1:TM){
                bosses[j][l]=0;
              }
            }
          }
                    
        //noninteger(sub)chars
        for(j in 1:Nsub){
           if(i==subchars[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == subchars[j][1]){//election id 
                    subs[j][l]=subpower[t][l];
                    //print("hit nonint charid",i-1," at ",t);
                 }else{
                    subs[j][l]=0;
                 }
               }

//               if(t==subchars[j][1]){//nointtitle charm time independent
//                noninttitle[i]=noninttitlepow[t];
//               }

            }else{
              for(l in 1:TM){
                subs[j][l]=0;
              }
            }
        }

        dth[i]=sum(mains)+sum(bosses)+sum(subs)+indivisual[i];
        //dth[i]=indivisual[i];
        //print("maincharpower",maincharpower);
        //print("boss",bosspower);
        //print("sub",subpower);
        //print("titlepow",titlepow);
        //print("mains",mains);
        //print("bosses",bosses);        
        //print("subs",subs);        
        //print("title",title);        
        }

//        print("----dth--",t,"-----",dth);       
        if(t==1){
                chars_vote_normal1~dirichlet(dth);
        {% for t2 in range(2,T1) %}
        }else if(t=={{t2}}){
                chars_vote_normal{{t2}}~dirichlet(dth);
        {%- endfor %}                
        }else{
        }
      }
}
  
