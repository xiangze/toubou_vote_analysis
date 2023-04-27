data {
  int<lower=0> T;//総投票回数
  int<lower=0> TM;//影響力の期間幅
  int<lower=0> Nchar[T];//投票回ごとのキャラクター数
  int<lower=0> Ncharmax;//キャラクター数の最大値
  int<lower=0> Nmain;//自機の総登場数
  int<lower=0> Nboss;//ボスの総登場数
  int<lower=0> Nsub;//非整数作品の総登場数

  int<lower=0> Nbook;//書籍作品総登場数
  int<lower=0> Nhifuu;//
  int<lower=0> Nmisc;

  //テンプレートで投票回ごとに異なる正規化した投票数の要素数(キャラクター数)を設定する
  {% for t in range(1,T1) %}
  simplex [Nchar[{{t}}]] chars_vote_normal{{t}};  
  {%- endfor %}                

  int mainchars[Nmain,2] ;//voteid(of int title), charid
  int bosschars[Nboss,3] ;//voteid(of int title), charid(boss), bosslevel
  int subchars [Nsub,2];//voteid(of nonint title), charid

  int bookchars [Nbook];
  int hihuuhars [Nhifuu];
  int miscchars [Nmisc];

}
parameters {
  matrix <lower=0>[T,TM] maincharpower;//coef of integer title main characters 
  matrix <lower=0>[T,TM] bosspower; //coef of integer title bosses
  matrix <lower=0>[T,TM] subpower;// coef of noninteger title members
  vector <lower=0>[Ncharmax] indivisual;  // indivisual charm

  real <lower=0> mu_i,mu_m,mu_b,mu_s;
  real <lower=0> sigma_i,sigma_m,sigma_b,sigma_s;

  real <lower=0> bookpow,hifuupow,miscpow;
}

model {
   //係数の事前分布の設定　正規分布に従いその平均、分散は指数分布、studentのt分布を使う
  mu_i~exponential(50);
  mu_m~exponential(100);
  mu_b~exponential(100);
  mu_s~exponential(100);
  
  sigma_i~student_t(4,0,100);
  sigma_m~student_t(4,0,100);
  sigma_b~student_t(4,0,100);
  sigma_s~student_t(4,0,100);
  //
   for(i in 1:Ncharmax){
    indivisual[i]~normal(mu_i,sigma_i);
  }

  for(t in 1:T){//tは投票回のインデックス
    //その他の事前分布の設定、指数分布を使う
      bookpow~exponential(10);
      hifuupow~exponential(10);
      miscpow~exponential(1);

      for(l in 1:TM){
        maincharpower[t,l]~normal(mu_m,sigma_m);
        bosspower[t,l]~normal(mu_b,sigma_b);
        subpower[t,l]~normal(mu_s,sigma_s);
      }

      vector[Nchar[t]] dth;
  
      for(i in 1:Nchar[t]){//i は個体のインデックス
          matrix[Nmain,TM] mains;
          matrix[Nboss,TM] bosses;
          matrix[Nsub,TM] subs;
          real book,hifuu,misc;

        //整数作品自機
        for(j in 1:Nmain){
           if((i-1)==mainchars[j][2]){//charidが一致した場合
               for(l in 1:TM){
                if( t-l+1 == mainchars[j][1]){//投票回が一致した場合
                    mains[j][l]=maincharpower[t][l];
                    //print("hit maincharpower",i-1,",",l,"\n");
                }else{
                    mains[j][l]=0;
                }
              }
              //print("hit charid",i-1);
            }else{//それ以外は係数0
              for(l in 1:TM){
                mains[j][l]=0;
              }
            }
        }
        //整数作品bosses
        for(j in 1:Nboss){
           if((i-1)==bosschars[j][2]){//charidが一致した場合
               for(l in 1:TM){
                if( t-l+1 == bosschars[j][1]){//投票回が一致した場合
                    bosses[j][l]=bosspower[t][l]*bosschars[j][3];//bosslevel*係数
                    //print("hit boss charid",i-1," at ",t);
                }else{
                    bosses[j][l]=0;
                }
              }
            }else{//それ以外は係数0
              for(l in 1:TM){
                bosses[j][l]=0;
              }
            }
          }
                    
        //非整数作品キャラクター
        for(j in 1:Nsub){
           if((i-1)==subchars[j][2]){//charidが一致した場合
               for(l in 1:TM){
                if( t-l+1 == subchars[j][1]){//投票回が一致した場合
                    subs[j][l]=subpower[t][l];
                    //print("hit nonint charid",i-1," at ",t);
                 }else{
                    subs[j][l]=0;
                 }
               }
            }else{//それ以外は係数0
              for(l in 1:TM){
                subs[j][l]=0;
              }
            }
        }
        //書籍登場の項
        for(j in 1:Nbook){
          if((i-1)==bookchars[j]){//charidが一致した場合
              book=bookpow;
          }else{
              book=0;
          }
        }
        //秘封倶楽部の項
        for(j in 1:Nhifuu){
          if((i-1)==hifuuchars[j]){//charidが一致した場合
              hifuu=hifuupow;
          }else{
              hifuu=0;
          }
        }
        //その他の項
        for(j in 1:Nmisc){
          if((i-1)==miscchars[j]){//charidが一致した場合
            misc=miscpow;
          }else{
            misc=0;
          }
        }
        //全ての項の和+個体項
        dth[i]=sum(mains)+sum(bosses)+sum(subs)+hifuu+book+misc+indivisual[i];
        }

//        print("----dth--",t,"-----",dth);       
//ディリクレ分布からの乱数生成　回ごとに次元(キャラクター数)が異なるのでテンプレートで対応する
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
  
