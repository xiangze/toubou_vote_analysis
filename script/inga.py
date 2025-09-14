#因果推論
import numpy as np, pandas as pd, pymc as pm, aesara.tensor as at
import seaborn as sns
import semopy 
from sklearn import datasets

#交絡 X が観測されていて、無交絡（Conditional Ignorability） が妥当。
def backdoor(df,X_cols = ["x1", "x2", "x3"]):# 交絡の列):
    X = df[X_cols].values
    t = df["t"].values
    y = df["y"].values
    n, p = X.shape

    with pm.Model() as m_gcomp:
        alpha = pm.Normal("alpha", 0, 2)
        beta_t = pm.Normal("beta_t", 0, 2)
        beta = pm.Normal("beta", 0, 1, shape=p)
        sigma = pm.HalfNormal("sigma", 1)

        mu = alpha + beta_t * t + at.dot(X, beta)
        pm.Normal("y_obs", mu, sigma, observed=y)

        idata = pm.sample(tune=1000, target_accept=0.9, chains=4)

    # g-computation: 同じXで t=1 / t=0 を差し替えて平均
    post = idata.posterior
    # broadcast: (chain, draw, 1) で形を合わせる
    alpha_s = post["alpha"].values[..., None]
    beta_t_s = post["beta_t"].values[..., None]
    beta_s   = post["beta"].values[..., None, :]  # (..., p)
    X_ = X[None, None, :, :]                      # (1,1,n,p)

    mu1 = alpha_s + beta_t_s*1 + (beta_s * X_).sum(-1)  # (..., n)
    mu0 = alpha_s + beta_t_s*0 + (beta_s * X_).sum(-1)
    ate_g = (mu1 - mu0).mean(axis=(-2,-1))  # 平均ATE（chain,draw平均）
    ate_point = ate_g.mean()
    ci = np.quantile(ate_g.reshape(-1), [0.025, 0.975])
    print(ate_point, ci)
    return ate_point,ci

#傾向スコア
#使いどころ：無交絡が妥当、回帰指定に自信がない/柔軟な調整をしたい。
#推定量：IPTW（安定化重みで分散低減）。バランス改善をチェック（SMD）必須
def propency_sore(X,t):
    # まず e(x)=P(t=1|X) のベイズロジスティック回帰
    with pm.Model() as m_ps:
        a = pm.Normal("a", 0, 2)
        b = pm.Normal("b", 0, 1, shape=p)
        logit_p = a + at.dot(X, b)
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p))
        pm.Bernoulli("t_obs", p, observed=t)
        ps_idata = pm.sample(tune=1000, target_accept=0.9, chains=4)

    e_hat = ps_idata.posterior["p"].mean(dim=("chain","draw")).values  # n次元
    # 安定化重み
    p_t = t.mean()
    sw = np.where(t==1, p_t/e_hat, (1-p_t)/(1-e_hat))

    # 自己正規化IPTWでATE
    num = (sw * (t*y / e_hat - (1-t)*y / (1-e_hat))).sum()
    den = sw.sum()
    ate_iptw = num / den
    print(ate_iptw)
    return ate_iptw

# Doubly Robust（AIPW / DR 推定）
#使いどころ：psモデルかアウトカムモデルのどちらか一方が正しければ一致推定量。
#推定量：AIPW で μ₁(x), μ₀(x) と e(x) を併用。
# アウトカム回帰（t と X を入れる）
def DoublyRobust(X,t):
    with pm.Model() as m_y:
        a = pm.Normal("a", 0, 2)
        bt = pm.Normal("bt", 0, 2)
        b = pm.Normal("b", 0, 1, shape=p)
        s = pm.HalfNormal("s", 1)
        mu = a + bt*t + at.dot(X, b)
        pm.Normal("y_obs", mu, s, observed=y)
        y_idata = pm.sample(tune=1000, target_accept=0.9, chains=4)

    # 予測平均（t=1/0 を差し替え）
    post = y_idata.posterior
    a_s  = post["a"].values[..., None]
    bt_s = post["bt"].values[..., None]
    b_s  = post["b"].values[..., None, :]
    X_   = X[None, None, :, :]

    mu1 = a_s + bt_s*1 + (b_s*X_).sum(-1)
    mu0 = a_s + bt_s*0 + (b_s*X_).sum(-1)
    mu1_hat = mu1.mean(axis=(0,1))  # n次元
    mu0_hat = mu0.mean(axis=(0,1))

    e_hat = ps_idata.posterior["p"].mean(dim=("chain","draw")).values

    # AIPW 推定量
    aipw = (mu1_hat - mu0_hat
            + t*(y - mu1_hat)/e_hat
            - (1-t)*(y - mu0_hat)/(1-e_hat)).mean()
    print(aipw)
    return aipw 

#使いどころ：パネル/繰り返し横断で政策介入など。並行トレンド仮定がキモ。
#最小モデル：個体効果＋時点効果＋交互作用（処置群×事後
def DiD(df):
    # df: columns [y, treated (個体固定), post (時点固定), unit, time]
    units = df["unit"].astype("category").cat.codes.values
    times = df["time"].astype("category").cat.codes.values
    treated = df["treated"].values
    post = df["post"].values
    y = df["y"].values
    U = units.max()+1
    T = times.max()+1

    with pm.Model() as m_did:
        # 個体・時点ランダム効果（ガウス）で二重固定効果の近似
        sigma_u = pm.HalfNormal("sigma_u", 1)
        sigma_t = pm.HalfNormal("sigma_t", 1)
        u = pm.Normal("u", 0, sigma_u, shape=U)
        v = pm.Normal("v", 0, sigma_t, shape=T)

        tau = pm.Normal("tau", 0, 1)  # 介入効果
        alpha = pm.Normal("alpha", 0, 2)
        sigma = pm.HalfNormal("sigma", 1)

        mu = alpha + u[units] + v[times] + tau * (treated * post)
        pm.Normal("y_obs", mu, sigma, observed=y)
        idata_did = pm.sample(target_accept=0.9, chains=4)

    tau_post = idata_did.posterior["tau"].values.reshape(-1)
    print(tau_post.mean(), np.quantile(tau_post, [0.025,0.975]))
    return tau_post

def control_variables(df):
    X_cols = ["x1","x2"]; X = df[X_cols].values
    z = df["z"].values
    D = df["t"].values.astype(float)  # 連続/確率的処置でも可
    Y = df["y"].values
    n, p = X.shape

    with pm.Model() as m_iv:
        # 第一段
        d0 = pm.Normal("d0", 0, 2)
        dz = pm.Normal("dz", 0, 2)
        dx = pm.Normal("dx", 0, 1, shape=p)
        sigma_D = pm.HalfNormal("sigma_D", 1)
        mu_D = d0 + dz*z + at.dot(X, dx)
        pm.Normal("D_obs", mu_D, sigma_D, observed=D)

        # 第二段（制御関数項）
        b0 = pm.Normal("b0", 0, 2)
        tau = pm.Normal("tau", 0, 2)     # 目的の因果効果
        bx = pm.Normal("bx", 0, 1, shape=p)
        sigma_Y = pm.HalfNormal("sigma_Y", 1)
        rho = pm.Uniform("rho", lower=-0.99, upper=0.99)

        cf = (D - mu_D) * (sigma_Y / sigma_D) * rho
        mu_Y = b0 + tau*D + at.dot(X, bx) + cf
        pm.Normal("Y_obs", mu_Y, sigma_Y*pm.math.sqrt(1 - rho**2), observed=Y)

        idata_iv = pm.sample(target_accept=0.9, chains=4)

    tau_post = idata_iv.posterior["tau"].values.reshape(-1)
    print(tau_post.mean(), np.quantile(tau_post,[0.025,0.975]))
    return tau_post

def RDD(df):
    c = df["running"].quantile(0.5)     # 例：既知の閾値
    h = df["running"].std() * 0.5       # 簡易帯域幅（要調整）
    mask = np.abs(df["running"] - c) <= h
    dat = df.loc[mask].copy()
    x = (dat["running"].values - c)
    t = (dat["running"].values >= 0).astype(int)  # 右側=処置  ※実際は割当規則に合わせる
    y = dat["y"].values

    with pm.Model() as m_rdd:
        alpha = pm.Normal("alpha", 0, 5)
        tau = pm.Normal("tau", 0, 5)       # 閾値でのジャンプ＝局所ATE
        bL = pm.Normal("bL", 0, 5)
        bR = pm.Normal("bR", 0, 5)
        sigma = pm.HalfNormal("sigma", 2)

        # 片側で傾きが異なる局所線形
        mu = alpha + tau*t + bL*x + (bR - bL)*(t*x)
        pm.Normal("y_obs", mu, sigma, observed=y)
        idata_rdd = pm.sample(target_accept=0.9, chains=4)

    tau_post = idata_rdd.posterior["tau"].values.reshape(-1)
    print(tau_post.mean(), np.quantile(tau_post,[0.025,0.975]))
    return tau_post

#https://qiita.com/ka201504/items/7edff7233869cd88a9cc
def SEM(df,outfilename="SEMout.png",view=False):
    df_std = df.apply(lambda x: (x-x.mean())/x.std(), axis=0)
    if(view):
        df_std_corr = df_std.corr()
        sns.heatmap(df_std_corr, cmap="coolwarm", vmin=-1, vmax=1, annot=True)
    # 仮説モデル
    model = '''
        # 測定方程式（潜在変数 =~ 観測変数）
        Charm =~ charpoint + musicpoint +
        Capability =~ Jumps + Situps + Chins
        Body =~ Waist + Weight

        # 構造方程式（目的変数 ~ 説明変数、潜在or観測どちらもOK）
        Chins ~ Capability + Body
        Situps ~Capability + Body
        Jumps ~ Capability + Body

        # 共変関係（双方向、潜在or観測どちらもOK）
        Chins ~~ Situps
        Situps ~~ Jumps
        Chins ~~ Jumps
        Weight ~~ Waist
        '''
    mod = semopy.Model(model)
    res = mod.fit(df_std)
    inspect = mod.inspect()
    if(view):
        print(inspect)

    g = semopy.semplot(mod, outfilename, plot_covs=True, engine="dot")

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('arg1', type=str, default="sample.csv")
    parser.add_argument('--method', type=str, default="DiD")
    parser.add_argument('--test', type=bool, default=False)
    args = parser.parse_args()
    
    data=pd.read_csv(args.name)
    if(args.test):
        import patsy as pt
        # 交絡行列Xのワンライナー作成（カテゴリ含む）
        y = data["y"].values
        t = data["t"].values
        X = pt.dmatrix("0 + x1 + x2 + C(cat1) + bs(x3, df=4)", data, return_type="dataframe").values
    else:
        X=data["X"]
        t=data["t"]

    method=args.method
    if(method=="SEM"):
        SEM(data)
    if(method=="DiD"):
        DiD(data)
    elif(method=="backdoor"):
        backdoor(data,X_cols = ["x1", "x2", "x3"])
    elif(method=="RDD"):
        RDD(data)        
    elif("keikou" in method or "propency" in method):
        propency_sore(X,t)
    elif("control" in method):
        control_variables(data)
    else:
        DoublyRobust(X,t)

    