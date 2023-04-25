data {
  int<lower=0> T;//総投票回数
  int<lower=0> TM;//影響力の期間幅
   int<lower=0> Nmusic[T];//投票回ごとの楽曲数
  int<lower=0> Nmusicmax;//楽曲数の最大値

  //登場順にソートされた正規化楽曲投票結果 
  //回ごとに楽曲数)が異なるのでテンプレートで書いている
  {% for t in range(1,T1) %}
  simplex [Nmusic[{{t}}]] vote_normal{{t}};  
  {%- endfor %}                

    int electionnum [Nmusicmax];//投票の開催番号
    int order   [Nmusicmax];//登場ステージ(道中曲とボス曲は同じ)
    //flags 楽曲ごとにあり0か1の値をとる
    int isinteger     [Nmusicmax];
    int isnoninteger [Nmusicmax];
    int isbook  [Nmusicmax];
    int isCD    [Nmusicmax];
    int ishifuu [Nmusicmax];
    int isold[Nmusicmax];
    int isseihou[Nmusicmax];
    int isother [Nmusicmax];
    int isoriginal [Nmusicmax];
}

parameters {
  matrix <lower=0>[T,TM] inttitlepow; //整数タイトルの係数
  matrix <lower=0>[T,TM] noninttitlepow; //非整数タイトルの係数
  //sairoku 再録曲(未実装)
  real   <lower=0> bookpow,hifuupow,CDpow;//書籍、秘封、CD作品の係数
  real   <lower=0> oldpow,otherpow,orgpow,seihoupow;//旧作、その他、オリジナル、西方の係数
  vector <lower=0>[Nmusicmax] indivisual;  //個別の係数
  real <lower=0> mu_t,mu_i;//整数,非整数タイトルの係数の平均値
  real <lower=0> sigma_t,sigma_i;//整数,非整数タイトルの係数の分散
 }

model {
  //整数作品、非整数作品の事前分布の設定　正規分布に従いその平均、分散は指数分布、studentのt分布を使う
  mu_t~exponential(10);;
  mu_i~exponential(10);

  sigma_i~student_t(4,0,20);
  sigma_t~student_t(4,0,20);
  //その他の事前分布の設定、指数分布を使う
    indivisual~exponential(0.1);
    bookpow~exponential(10);
    hifuupow~exponential(10);
    CDpow~exponential(10);
    oldpow~exponential(10);
    otherpow~exponential(10);
    orgpow~exponential(10);

    real titlebase,noninttitlebase;

  for(t in 1:T){//tは投票回のインデックス
      vector[Nmusic[t]] dth;
      //整数作品、非整数作品の事前分布の設定
      inttitlepow[t]~normal(mu_t,sigma_t);//t is title index
      noninttitlepow[t]~normal(mu_i,sigma_i);//t is nonint title index

      for(i in 1:Nmusic[t]){//i は個体のインデックス
          vector[TM] inttitle;
          vector[TM] noninttitle;
          //vector[TM] sairoku;//再録
          real book, hifuu,CD,old,seihou,other,org;
        //整数作品、非整数作品の項
        for(l in 1:TM){//lは期間のインデックス
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
        //書籍、CD、秘封倶楽部、旧作、その他、オリジナル曲、西方の項
        book=bookpow*isbook[i];
        CD=CDpow*isCD[i];
        hifuu=hifuupow*ishifuu[i];
        old=oldpow*isold[i];
        other=otherpow*isother[i];
        org=orgpow*isoriginal[i];
        seihou=seihoupow*isseihou[i];
        //全ての項の和+個体項
        dth[i]=(sum(inttitle) +sum(noninttitle)
                    +hifuu+book+CD+old+other+org+seihou)+indivisual[i];

        }
        //print("----dth--",t,"-----",dth);     
        //ディリクレ分布からの乱数生成　回ごとに次元(楽曲数)が異なるのでテンプレートで対応する
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
  
