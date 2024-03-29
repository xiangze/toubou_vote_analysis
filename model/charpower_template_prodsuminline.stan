//https://stats.biopapyrus.jp/bayesian-statistics/stan/stan-block.html
//https://statmodeling.hatenablog.com/entry/state-space-model-many-terms
{% macro hit(out,Num, table,index,power) -%}
    for(j in 1:{{Num}}){
          if(({{index}}-1)=={{table}}[j]){
              {{out}}[j]={{power}};
          }else{
              {{out}}[j]=0;
          }
    }
{%- endmacro %}

{% macro hit1d(out, Num, table,index,power) -%}
      {{out}}=0;
      for(j in 1:{{Num}}){
        //charid& title (time independent)
        if((({{index}}-1)=={{table}}[j][2])){
               {{out}}={{power}}[{{table}}[j][1]];
            }
        }
{%- endmacro %}

//matrix  hit2d(int Num,int [,]table,int index,int t,int TM,matrix power){
{% macro hit2d(out, Num,table,index,t,TM,power) -%}
          for(j in 1:{{Num}}){
           if(({{index}}-1)=={{table}}[j][2]){//charid
               for(l in 1:{{TM}}){
                if( t-l+1 == {{table}}[j][1]){//vote id
                    {{out}}[j][l]={{power}}[t][l];
                }else{
                    {{out}}[j][l]=0;
                }
              }
            }else{
              for(l in 1:{{TM}}){
                {{out}}[j][l]=0;
              }
            }
          }
{%- endmacro %}

/*functions{
  vector hit(int Num,int []table,int index,real power){
    vector [Num]out;
      for(j in 1:Num){
          if((index-1)==table[j]){
              out[j]=power;
          }else{
              out[j]=0;
          }
      }
    return out;
  }
  real hit1d(int Num,int Tmax,int [,]table,int index,vector power){
      for(j in 1:Num){
        for(t in 1:Tmax){//t is title index
        //charid& title (time independent)
//        if(((index-1)==table[j][2])&& (t==table[j][1])){
        if((index-1)==table[j][2]){
               return power[table[j][1]];
            }
        }
      }
        return 0;
  }

matrix  hit2d(int Num,int [,]table,int index,int t,int TM,matrix power){
          matrix [Num,TM] out;
          for(j in 1:Num){
           if((index-1)==table[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == table[j][1]){//vote id
                    out[j][l]=power[t][l];
                }else{
                    out[j][l]=0;
                }
              }
            }else{
              for(l in 1:TM){
                out[j][l]=0;
              }
            }
          }
        return out;
  }
}
*/

data {
  int<lower=0> T;//num of elections
  int<lower=0> TM;//time window size
  int<lower=0> Nchar[T];//num. of characters 
  int<lower=0> Ncharmax;//num. of characters 
//  int<lower=0> Nmusic;//num. of characters 
  int<lower=0> Nmain;// num. of integer main characters 
  int<lower=0> Nboss;// num. of integer bosses
  int<lower=0> Nsub;// num. of noninteger characters 

  int<lower=0> Nbook;
  int<lower=0> Nhifuu;
  int<lower=0> Nmisc;

  //normalized vote num. 1:rate
  {% for t in range(1,T1) %}
  simplex [Nchar[{{t}}]] chars_vote_normal{{t}};  
  {%- endfor %}                

  int  mainchars[Nmain,2] ;//voteid(of int title), charid
  int  bosschars[Nboss,3] ;//voteid(of int title), charid(boss), bosslevel
  int subchars [Nsub,2];//voteid(of nonint title), charid

  int bookchars [Nbook];
  int hifuuchars [Nhifuu];
  int miscchars [Nmisc];

//  matrix<int=1>  [Nmusic][T] musics;
}
parameters {
  matrix <lower=0>[T,TM] maincharpower;//coef of integer title main characters 
  matrix <lower=0>[T,TM] bosspower; //coef of integer title bosses
  matrix <lower=0>[T,TM] subpower;// coef of noninteger title members
  vector <lower=0>[T] titlepow; //coef of integer title
  vector <lower=0>[T] noninttitlepow; //coef of integer title
  vector <lower=0>[Ncharmax] indivisual;  // indivisual charm
  real <lower=0> bookpow,hifuupow,miscpow;

  real <lower=0> mu_i,mu_m,mu_b,mu_s,mu_t;
  real <lower=0> sigma_i,sigma_m,sigma_b,sigma_s,sigma_t;
 
}

//transformed parameters {
//}

model {
//  mu_i~exponential(10);
  mu_m~exponential(10);
  mu_b~exponential(10);
  mu_s~exponential(10);;
  mu_t~exponential(10);
  
//  sigma_i~student_t(4,0,20);
  sigma_m~student_t(4,0,20);
  sigma_b~student_t(4,0,20);
  sigma_s~student_t(4,0,20);
  sigma_t~student_t(4,0,20);

    indivisual~exponential(30);
    bookpow~exponential(10);
    hifuupow~exponential(10);
    miscpow~exponential(1);
    
    real titlebase,noninttitlebase;

  for(t in 1:T){//election
        vector[Nchar[t]] dth;

      titlepow[t]~normal(mu_t,sigma_t);//t is title index
      noninttitlepow[t]~normal(mu_t,sigma_t);//t is nonint title index

      for(l in 1:TM){
        maincharpower[t,l]~normal(mu_m,sigma_m);//uniform(1e-6,1000);
        bosspower[t,l]~normal(mu_b,sigma_b);//uniform(1e-6,1000);
        subpower[t,l]~normal(mu_s,sigma_s);//uniform(1e-6,1000);
      }

      for(i in 1:Nchar[t]){//indivisual character
          matrix[Nmain,TM] mains;
          matrix[Nboss,TM] bosses;
          matrix[Nsub,TM] subs;
          vector[Nbook] book;
          vector[Nhifuu] hifuu;
          vector[Nmisc] misc;

//        mains=hit2d(Nmain,mainchars,i,t,TM,maincharpower);
//        subs=hit2d(Nsub,subchars,i,t,TM,subpower);
    {{ hit2d("mains", "Nmain","mainchars","i","t","TM","maincharpower") }}
    {{ hit2d("subs" , "Nsub", "subchars","i","t","TM","subpower") }}
//        book=hit(Nbook,bookchars,i,bookpow);
//        hifuu=hit(Nhifuu,hifuuchars,i,hifuupow);
//        misc=hit(Nmisc,miscchars,i,miscpow);
        {{hit("book","Nbook","bookchars","i","bookpow")}}        
        {{hit("hifuu","Nhifuu","hifuuchars","i","hifuupow")}}        
        {{hit("misc","Nmisc","miscchars","i","miscpow")}}        

        //bosses
        for(j in 1:Nboss){
           if((i-1)==bosschars[j][2]){//charid
               for(l in 1:TM){
                if( t-l+1 == bosschars[j][1]){//election id 
                    bosses[j][l]=bosspower[t][l]*bosschars[j][3];//bosslevel
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

        //titlebase=hit1d(Nboss,Nchar[t],bosschars,i,titlepow);
        //noninttitlebase=hit1d(Nsub,Nchar[t],subchars,i,noninttitlepow);
       {{hit1d("titlebase", "Nboss", "bosschars","i","titlepow") }}
       {{hit1d("noninttitlebase", "Nsub", "subchars","i","noninttitlepow") }}

        dth[i]=(sum(mains)+sum(bosses)+titlebase+sum(subs)
                    +noninttitlebase
                    +sum(hifuu)+sum(book)+sum(misc))*indivisual[i];
                    
/*
        if(coef==0.){
          print("t=",t);
          print("index",i);
          print("titlebase[i]",titlebase[i]);
          if(t==1){
            print("vote_normal",chars_vote_normal1[i]);
           {% for t2 in range(2,T1) %}
           }else if(t=={{t2}}){
            print("vote_normal",chars_vote_normal{{t2}}[i]);
            {%- endfor %}                
            }else{
            }
          
        //print("mains",mains);
        //print("bosses",bosses);        
        //print("subs",subs);        
        //print("misc",misc);        
        }
*/
        //print("maincharpower",maincharpower);
        //print("boss",bosspower);
        //print("sub",subpower);
        //print("titlepow",titlepow);
        //print("mains",mains);
        //print("bosses",bosses);        
        //print("subs",subs);        
        //print("coef",coef);        

        }
        //print("----dth--",t,"-----",dth);     

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
  
