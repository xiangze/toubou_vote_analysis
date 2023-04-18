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
  int<lower=0> Nmusic[T];//num. of characters 
  int<lower=0> Nmusicmax;//num. of characters 

  //normalized vote num. 1:rate
  {% for t in range(1,T1) %}
  simplex [Nmusic[{{t}}]] vote_normal{{t}};  
  {%- endfor %}                

    int electionnum [Nmusicmax];//election num
    //flags
    int isinteger     [Nmusicmax];
    int isnoninteger [Nmusicmax];
    int order   [Nmusicmax];
    int isbook  [Nmusicmax];
    int isCD    [Nmusicmax];
    int ishifuu [Nmusicmax];
    int isold[Nmusicmax];
    int isseihou[Nmusicmax];
    int isother [Nmusicmax];
    int isoriginal [Nmusicmax];
}

parameters {
  matrix <lower=0>[T,TM] inttitlepow; //coef of integer title
  matrix <lower=0>[T,TM] noninttitlepow; //coef of integer title
  //sairoku
  real   <lower=0> bookpow,hifuupow,CDpow;
  real   <lower=0> oldpow,otherpow,orgpow,seihoupow;
  vector <lower=0>[Nmusicmax] indivisual;  // indivisual charm
  real <lower=0> mu_t,mu_i;
  real <lower=0> sigma_t,sigma_i;
 }

//transformed parameters {
//}

model {
  mu_t~exponential(10);;
  mu_i~exponential(10);

  sigma_i~student_t(4,0,20);
  sigma_t~student_t(4,0,20);
  
    indivisual~exponential(0.1);
    bookpow~exponential(10);
    hifuupow~exponential(10);
    CDpow~exponential(10);
    oldpow~exponential(10);
    otherpow~exponential(10);
    orgpow~exponential(10);

    real titlebase,noninttitlebase;

  for(t in 1:T){//election
        vector[Nmusic[t]] dth;
//      for(l in 1:TM){
      inttitlepow[t]~normal(mu_t,sigma_t);//t is title index
      noninttitlepow[t]~normal(mu_i,sigma_i);//t is nonint title index

      for(i in 1:Nmusic[t]){//indivisual character
          vector[TM] inttitle;
          vector[TM] noninttitle;
          //vector[TM] sairoku;//再録
          real book, hifuu,CD,old,seihou,other,org;

        for(l in 1:TM){
            if(isinteger[i]&& (t==electionnum[i]+l-1)){
                inttitle[l]=order[i]*inttitlepow[electionnum[i]][l];
            }else{
                inttitle[l]=0;
            }
            if(isnoninteger[i]&&  (t==electionnum[i]+l-1)){
                noninttitle[l]=noninttitlepow[electionnum[i]][l];                
            }else{
                noninttitle[l]=0;
            }
        }

        book=bookpow*isbook[i];
        CD=CDpow*isCD[i];
        hifuu=hifuupow*ishifuu[i];
        old=oldpow*isold[i];
        other=otherpow*isother[i];
        org=orgpow*isoriginal[i];
        seihou=seihoupow*isseihou[i];

        real coef=(sum(inttitle) +sum(noninttitle) +hifuu+book+CD+old+other+org+seihou);
        dth[i]=coef*indivisual[i];
                   
        if(coef==0.){
        print("t,i=",t,",",i);            
            if(indivisual[i]==0){
                print("indivisual[i]=",indivisual[i]);
            }
/*            
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
            */
        }

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
                vote_normal1~dirichlet(dth);
        {% for t2 in range(2,T1) %}
        }else if(t=={{t2}}){
                vote_normal{{t2}}~dirichlet(dth);
        {%- endfor %}                
        }else{
        }
      }
}
  
