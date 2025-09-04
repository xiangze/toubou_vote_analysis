import pymc as pm
import aesara.tensor as at
import numpy as np

def music_sum(data):
    with pm.Model() as music_model:

        # --------------------
        #  ハイパーパラメータ
        # --------------------
        mu_t  = pm.Exponential("mu_t",  lam=10.0)
        mu_i  = pm.Exponential("mu_i",  lam=10.0)
        sigma_t = pm.HalfStudentT("sigma_t", nu=4, sigma=20.0)
        sigma_i = pm.HalfStudentT("sigma_i", nu=4, sigma=20.0)

        # --------------------
        #  係　数
        # --------------------
        inttitlepow  = pm.Normal("inttitlepow",
                                mu=mu_t, sigma=sigma_t,
                                shape=(T, TM))
        noninttitlepow = pm.Normal("noninttitlepow",
                                mu=mu_i, sigma=sigma_i,
                                shape=(T, TM))

        # 書籍・CD など作品属性ごとの係数
        bookpow   = pm.Exponential("bookpow",   lam=10.0)
        hifuupow  = pm.Exponential("hifuupow",  lam=10.0)
        CDpow     = pm.Exponential("CDpow",     lam=10.0)
        oldpow    = pm.Exponential("oldpow",    lam=10.0)
        otherpow  = pm.Exponential("otherpow",  lam=10.0)
        orgpow    = pm.Exponential("orgpow",    lam=10.0)
        seihoupow = pm.Exponential("seihoupow", lam=10.0)

        # 楽曲個別係数
        indivisual = pm.Exponential("indivisual",
                                    lam=0.1,
                                    shape=(Nmusic_max,))

        # --------------------
        #  各投票回ごとの尤度
        # --------------------
        for t in range(data["T"]):

            n_i  = Nmusic[t]                 # その回の楽曲数
            idx  = slice(0, n_i)             # indivisual やフラグの該当部分

            # ----- 作品タイトルの影響（整数／非整数） -----
            #   inttitle_contrib[i] = Σ_l 1{条件} * order_i * inttitlepow[electionnum_i-1,l]
            #   Stan の 1-index → Python の 0-index 差に注意
            int_contrib  = at.zeros((n_i,))
            nonint_contrib = at.zeros((n_i,))
            for l in range(TM):
                cond = at.eq(t + 1, electionnum[idx] + l)           # +1 で Stan に合わせる
                int_contrib  += cond * order_[idx] * inttitlepow[electionnum[idx]-1, l]
                nonint_contrib += cond * noninttitlepow[electionnum[idx]-1, l]

            # ----- 作品属性フラグの影響 -----
            attr = (bookpow   * isbook[idx] +
                    hifuupow  * ishifuu[idx] +
                    CDpow     * isCD[idx] +
                    oldpow    * isold[idx] +
                    otherpow  * isother[idx] +
                    orgpow    * isoriginal[idx] +
                    seihoupow * isseihou[idx])

            # ----- 個別項を足し合わせ Dirichlet パラメータを作成 -----
            alpha_t = (int_contrib + nonint_contrib + attr +
                        indivisual[idx])

            # 安全のため正値化（Stan 版は正数になるという前提）
            alpha_t_pos = pm.math.softplus(alpha_t)

            pm.Dirichlet(f"vote_normal_{t+1}",
                        a=alpha_t_pos,
                        observed=vote_normals[t])

        # -------------
        #  サンプリング
        # -------------
        trace = pm.sample(2000, tune=2000, target_accept=0.9, cores=4)
    return trace

if __name__=="__main__":
    # 例: numpy 配列または list
    T            = len(vote_normals)          # 総投票回数
    TM           = ...                        # 影響力が残る期間幅
    Nmusic       = np.array([len(v) for v in vote_normals], dtype="int64")
    Nmusic_max   = Nmusic.max()

    # 作品属性フラグなど。Nmusic_max の長さでそろえて 0/1 を入れて下さい。
    electionnum  = np.array([...], dtype="int64")   # 1,2,... で Stan と同じインデックス
    order_       = np.array([...], dtype="float64") # 登場ステージ (整数 >0)
    isinteger    = np.array([...], dtype="int8")
    isnoninteger = np.array([...], dtype="int8")
    isbook       = ...
    isCD         = ...
    ishifuu      = ...
    isold        = ...
    isseihou     = ...
    isother      = ...
    isoriginal   = ...
