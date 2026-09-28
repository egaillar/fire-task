from pathlib import Path
import pandas as pd
import numpy as np

CSV_PATH = Path(__file__).parent / "parsed_data" / "parsed_slider_pref_final.csv"

if __name__ == "__main__":
    df = pd.read_csv(CSV_PATH)
    df = df[df["attn"] == 0].copy()

    df["response_scaled"] = 6.0 * (df["response"] / 100.0) - 3.0

    # ---- Image-wise mean ratings: mu_hat_i ----
    g = df.groupby("image")["response_scaled"]
    mu_hat_i = g.mean()          # indexed by image (n_images,)
    n_i = g.count().astype(int)  # number of ratings per image (n_images,)

    # mean of the latent distribution (empirical)
    mu_mean_hat = float(mu_hat_i.mean()) # scalar

    # ---- Global noise variance: pooled within-image residual variance (unbiased) ----
    # residuals around the image mean
    df = df.join(mu_hat_i.rename("mu_hat_i"), on="image")
    resid = df["response_scaled"].to_numpy(dtype=float) - df["mu_hat_i"].to_numpy(dtype=float)

    # degrees of freedom: sum_i (n_i - 1)
    dof = int((n_i - 1).sum()) # scalar

    sigma2 = float(np.sum(resid ** 2) / dof) # scalar
    sigma = float(np.sqrt(sigma2)) # scalar

    # # ---- Between-image variance of latent utilities: corrected for finite-sample noise ----
    # sample variance of observed image means (mu_hat_i)
    var_mu_hat = float(mu_hat_i.var(ddof=1))

    # correction term: E[sigma^2 / n_i] ≈ sigma2 * mean(1/n_i)
    mean_inv_n = float((1.0 / n_i).mean())
    var_mu = float(var_mu_hat - sigma2 * mean_inv_n)

    mu_sd = float(np.sqrt(var_mu))

    # # ---- Print / save the calibrated parameters ----
    print("Empirical calibration (unimodal Normal):")
    print(f"  mu (mean of mu_i):         {mu_mean_hat:.6f}")
    print(f"  var(mu_i):                 {var_mu:.6f}   (sd={mu_sd:.6f})")
    print(f"  sigma^2 (global noise):    {sigma2:.6f}   (sigma={sigma:.6f})")
    print(f"  I (# images):              {len(mu_hat_i)}")
    print(f"  N_obs (# ratings):         {len(df)}")
    print(f"  mean(n_i):                 {float(n_i.mean()):.3f}   min={int(n_i.min())}  max={int(n_i.max())}")
    
    # optional: these are the params you feed into simulate_world(mu_dist="normal")
    print("\nParameters for simulate_world(mu_dist='normal'):")
    print(f"  mu_dist='normal'")
    print(f"  mu_mean={mu_mean_hat}")
    print(f"  mu_sd={mu_sd}")
    print(f"  noise_sd={sigma}")
