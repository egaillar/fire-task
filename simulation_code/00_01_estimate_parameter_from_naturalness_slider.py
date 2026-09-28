from pathlib import Path
from sklearn.mixture import GaussianMixture
import numpy as np
import pandas as pd

CSV_PATH = Path(__file__).parent / "parsed_data" / "parsed_slider_nat_final.csv"

if __name__ == "__main__":
    df = pd.read_csv(CSV_PATH)
    df = df[df["attn"] == 0].copy()

    # guard: finite responses only
    df = df[np.isfinite(df["response"])].copy()

    # map slider 0-100 -> latent [-3, 3]
    df["response_scaled"] = 6.0 * (df["response"] / 100.0) - 3.0

    # ---- Image-wise mean ratings: mu_hat_i ----
    g = df.groupby("image")["response_scaled"]
    mu_hat_i = g.mean()          # (n_images,)
    n_i = g.count().astype(int)  # (n_images,)

    if len(mu_hat_i) < 2:
        raise ValueError("Need at least 2 images to fit a bimodal distribution.")

    # ---- Global noise variance: pooled within-image residual variance (unbiased) ----
    # residuals around the image mean
    df = df.join(mu_hat_i.rename("mu_hat_i"), on="image")
    resid = df["response_scaled"].to_numpy(dtype=float) - df["mu_hat_i"].to_numpy(dtype=float)

    dof = int((n_i - 1).sum())
    if dof <= 0:
        raise ValueError(
            "Not enough repeated ratings per image to estimate sigma^2 "
            "(need some images with n_i >= 2)."
        )

    sigma2 = float(np.sum(resid ** 2) / dof)
    sigma = float(np.sqrt(sigma2))

    # -----------------------------
    # Bimodal (2-component) fit to empirical mu_hat_i
    # -----------------------------
    X = mu_hat_i.to_numpy(dtype=float).reshape(-1, 1)

    gmm2 = GaussianMixture(
        n_components=2,
        random_state=0,
    ).fit(X)

    weights = gmm2.weights_.copy()          # (2,)
    means = gmm2.means_.ravel().copy()      # (2,)

    # covariances_: (2, 1, 1) for full in 1D
    covs = gmm2.covariances_
    if covs.ndim == 3:
        vars_ = covs[:, 0, 0].copy()
    else:
        # fallback for other covariance_types
        vars_ = np.array(covs).ravel().copy()

    # Sort components by mean for interpretability
    order = np.argsort(means)
    weights = weights[order]
    means = means[order]
    vars_ = vars_[order]

    bimodal_weight_low = float(weights[0])  # mixing weight for lower-mean mode
    bimodal_means = (float(means[0]), float(means[1]))
    bimodal_sds = (float(np.sqrt(vars_[0])), float(np.sqrt(vars_[1])))

    print("\nEmpirical calibration (bimodal Gaussian mixture):")
    print(f"  mixing weights:            {weights}")
    print(f"  component means:           {bimodal_means}")
    print(f"  component sds:             {bimodal_sds}")
    print(f"  sigma^2 (global noise):    {sigma2:.6f}   (sigma={sigma:.6f})")
    print(f"  I (# images):              {len(mu_hat_i)}")
    print(f"  N_obs (# ratings):         {len(df)}")
    print(f"  mean(n_i):                 {float(n_i.mean()):.3f}   min={int(n_i.min())}  max={int(n_i.max())}")

    # optional: these are the params you feed into simulate_world(mu_dist="bimodal")
    print("\nParameters for simulate_world(mu_dist='bimodal'):")
    print(f"  bimodal_weight={bimodal_weight_low}")
    print(f"  bimodal_means={bimodal_means}")
    print(f"  bimodal_sds={bimodal_sds}")
    print(f"  noise_sd={sigma}")
