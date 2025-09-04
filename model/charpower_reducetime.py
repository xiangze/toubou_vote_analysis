import pymc as pm
import aesara.tensor as at
import numpy as np

with pm.Model() as char_model:

    # -------------------------------
    # パラメータ（Stan parameters{}）
    # -------------------------------
    sigma = pm.Uniform("sigma",
                       lower=1e-6, upper=1000,
                       shape=(T, TM))      # 整数タイトル主役
    b     = pm.Uniform("b",
                       lower=1e-6, upper=1000,
                       shape=(T, TM))      # 整数タイトルボス
    s     = pm.Uniform("s",
                       lower=1e-6, upper=1000,
                       shape=(T, TM))      # 非整数タイトルメンバ
    eps   = pm.Uniform("eps",
                       lower=1e-6, upper=1000,
                       shape=(Nchar_max,)) # 個別魅力度

    # ----------------------------------------
    # 尤度（Stan model{} のループを Python 化）
    # ----------------------------------------
    for t in range(T):

        n_i = int(Nchar[t])       # 今回のキャラ数
        idx = slice(0, n_i)

        # --- タイトル寄与をゼロ初期化 ---
        alpha = at.zeros((n_i,))

        # --- 整数タイトル：主役 ---
        for l in range(TM):
            # 条件   (t+1-l == voteid) & (char==対象)
            hit = (t + 1 - l == mainchars[:, 0])  # bool (Nmain,)
            # mainchars[:,1] は charid
            contrib_vec = at.zeros((n_i,))
            contrib_vec = at.set_subtensor(
                contrib_vec[mainchars[hit, 1]],
                sigma[t, l])
            alpha += contrib_vec

        # --- 整数タイトル：ボス ---
        for l in range(TM):
            hit = (t + 1 - l == bosschars[:, 0])
            contrib_vec = at.zeros((n_i,))
            contrib_vec = at.set_subtensor(
                contrib_vec[bosschars[hit, 1]],
                b[t, l] * bosschars[hit, 2])
            alpha += contrib_vec

        # --- 非整数タイトル：メンバー ---
        for l in range(TM):
            hit = (t + 1 - l == subchars[:, 0])
            contrib_vec = at.zeros((n_i,))
            contrib_vec = at.set_subtensor(
                contrib_vec[subchars[hit, 1]],
                s[t, l])
            alpha += contrib_vec

        # --- 個別魅力度 ---
        alpha += eps[idx]

        # Dirichlet の concentration は正値必須
        alpha_pos = pm.math.softplus(alpha)

        pm.Dirichlet(f"chars_vote_{t+1}",
                     a=alpha_pos,
                     observed=chars_vote_normals[t])

    # -----------------
    # サンプリング設定
    # -----------------
    trace = pm.sample(2000, tune=2000,
                      target_accept=0.9,
                      cores=4, random_seed=42)
