import numpy as np
from numpy.random import default_rng, Generator
from scipy.stats import pearsonr
from typing import Literal, Tuple, Union, Optional

def _handle_rng(rng: Union[None, int, Generator]) -> Generator:
    if rng is None:
        rng = default_rng()
    elif isinstance(rng, int):
        rng = default_rng(rng)
    elif not isinstance(rng, Generator):
        raise TypeError("rng must be None, int, or numpy.random.Generator")
    return rng

def simulate_world(
    *,
    n_images: int,
    n_perceivers: int,
    n_simulations: int,
    n_judged_per_perceiver: int,
    mu_mean: float = 0.0,
    mu_sd: float = 1.0,
    noise_sd: float = 1.0,
    # --- new (backward-compatible) ---
    mu_dist: Literal["normal", "uniform", "bimodal"] = "normal",
    mu_uniform_low: float = -3.0,
    mu_uniform_high: float = 3.0,
    bimodal_weight: float = 0.5,
    bimodal_means: Tuple[float, float] = (-2.0, 2.0),
    bimodal_sds: Optional[Tuple[float, float]] = None,
    rng: Union[None, int, Generator] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Classical Thurstone-style world on a fixed latent scale:

        j_{i,p} ~ Normal(mu_i, noise_sd^2)

    The true image utilities mu_i are drawn independently for each simulation from
    one of:
        - normal:  mu_i ~ Normal(mu_mean, mu_sd^2)                 (default)
        - uniform: mu_i ~ Uniform(mu_uniform_low, mu_uniform_high)
        - bimodal: mu_i ~ mixture of two Normals with mixing weight bimodal_weight

    Each perceiver judges exactly n_judged_per_perceiver images (subset of n_images).
    Unjudged entries are NaN.

    Returns:
        img_mu: (S, I)        latent true image utilities mu_i, one world per simulation
        latent: (S, P, I)     latent judgments j_{i,p,s} (NaN where unjudged)
    """
    rng = _handle_rng(rng)

    # --- checks ---
    if n_images <= 0 or n_perceivers <= 0 or n_simulations <= 0:
        raise ValueError("n_images, n_perceivers, n_simulations must be positive")
    if not (1 <= n_judged_per_perceiver <= n_images):
        raise ValueError("n_judged_per_perceiver must be in [1, n_images]")
    if mu_sd < 0 or noise_sd < 0:
        raise ValueError("mu_sd and noise_sd must be non-negative")

    if mu_dist == "uniform":
        if not np.isfinite(mu_uniform_low) or not np.isfinite(mu_uniform_high):
            raise ValueError("mu_uniform_low/high must be finite")
        if mu_uniform_high <= mu_uniform_low:
            raise ValueError("mu_uniform_high must be > mu_uniform_low")

    if mu_dist == "bimodal":
        if not (0.0 < float(bimodal_weight) < 1.0):
            raise ValueError("bimodal_weight must be in (0,1)")
        m1, m2 = map(float, bimodal_means)
        if not (np.isfinite(m1) and np.isfinite(m2)):
            raise ValueError("bimodal_means must be finite")
        if bimodal_sds is None:
            s1 = s2 = float(mu_sd)
        else:
            s1, s2 = map(float, bimodal_sds)
        if s1 < 0 or s2 < 0:
            raise ValueError("bimodal_sds must be non-negative")
        # (allow s1 or s2 == 0 as a degenerate spike)

    I, P, S = n_images, n_perceivers, n_simulations

    # --- draw true image utilities (latent ground truth) ---
    if mu_dist == "normal":
        img_mu = rng.normal(loc=float(mu_mean), scale=float(mu_sd), size=(S, I))

    elif mu_dist == "uniform":
        img_mu = rng.uniform(low=float(mu_uniform_low), high=float(mu_uniform_high), size=(S, I))

    elif mu_dist == "bimodal":
        m1, m2 = map(float, bimodal_means)
        if bimodal_sds is None:
            s1 = s2 = float(mu_sd)
        else:
            s1, s2 = map(float, bimodal_sds)

        z = rng.random((S, I)) < float(bimodal_weight)  # True -> component 1, False -> component 2
        img_mu = np.where(
            z,
            rng.normal(loc=m1, scale=s1, size=(S, I)),
            rng.normal(loc=m2, scale=s2, size=(S, I)),
        )

    else:
        raise ValueError("mu_dist must be one of {'normal','uniform','bimodal'}")

    # --- exposure mask (S, P, I) ---
    judged_mask = np.zeros((S, P, I), dtype=bool)
    for s in range(S):
        for p in range(P):
            idx = rng.choice(I, size=n_judged_per_perceiver, replace=False)
            judged_mask[s, p, idx] = True
    assert np.all(judged_mask.sum(axis=2) == n_judged_per_perceiver)

    # --- latent judgments ---
    latent = np.full((S, P, I), np.nan, dtype=float)

    eps = rng.normal(loc=0.0, scale=float(noise_sd), size=(S, P, I))
    latent_full = img_mu[:, None, :] + eps  # (S,1,I) + (S,P,I) -> (S,P,I)

    latent[judged_mask] = latent_full[judged_mask]
    return img_mu, latent

def latent_to_ratings(
    latent: np.ndarray,
    *,
    cutpoints: np.ndarray,
) -> np.ndarray:
    """
    Convert latent judgments to integerratings using fixed cutpoints.

    Args:
        latent: np.ndarray, typically shape (S, P, I); can be any shape.
               Missing/unjudged entries should be NaN.
        cutpoints: length-6 increasing array defining thresholds for 7 categories.

    Returns:
        ratings: same shape as latent, int ratings.
    """
    cutpoints = np.asarray(cutpoints, dtype=float)
    if not np.all(np.diff(cutpoints) > 0):
        raise ValueError("cutpoints must be strictly increasing.")

    ratings = np.full(latent.shape, np.nan)

    mask = ~np.isnan(latent)
    ratings[mask] = np.digitize(latent[mask], cutpoints)

    return ratings


def latent_to_count(
    latent: np.ndarray,
    *,
    n_trials: int,
    n_shown: int,
    n_select: int,
    n_attn_check: int = 0,
    rng: Union[None, int, Generator] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generalized comparison from latent judgments with NO repeats across trials.

    For each (simulation s, perceiver p):
      - pool = { i : latent[s,p,i] is observed (not NaN) }
      - optionally require |pool| divisible by n_shown
      - create n_trials trials with no repeats across trials:
          * n_attn_check trials show (n_shown - 1) images
          * remaining trials show n_shown images
      - in each trial, select the top n_select by latent value
        (ties resolved deterministically by lower image index)

    Args:
        latent: (S, P, I) latent judgments with NaN for missing/unshown.
        n_trials: number of trials per (s,p).
        n_shown: number of images shown per normal trial (>=2).
        n_select: number of images selected per trial.
        n_attn_check: number of trials per (s,p) that show (n_shown - 1) images.
        rng: None, int seed, or numpy Generator.

    Returns:
      shown_counts:    (S,P,I) uint16 counts of how many times each image was shown
      selected_counts: (S,P,I) uint16 counts of how many times each image was selected
    """
    rng = _handle_rng(rng)

    if latent.ndim != 3:
        raise ValueError("latent must have shape (S, P, I)")
    S, P, I = latent.shape

    if n_trials <= 0:
        raise ValueError("n_trials must be positive")
    if n_shown < 2:
        raise ValueError("n_shown must be at least 2")
    if not (1 <= n_select <= n_shown):
        raise ValueError("n_select must be in [1, n_shown]")
    if not (0 <= n_attn_check <= n_trials):
        raise ValueError("n_attn_check must be in [0, n_trials]")
    if n_attn_check > 0 and n_select > (n_shown - 1):
        raise ValueError("If n_attn_check > 0, must have n_select <= n_shown - 1.")

    T = n_trials
    selected_counts = np.zeros((S, P, I), dtype=np.uint16)
    shown_counts = np.zeros((S, P, I), dtype=np.uint16)

    for s in range(S):
        for p in range(P):
            pool = np.flatnonzero(~np.isnan(latent[s, p])) # indices of observed images
            pool_size = pool.size

            # attention-check trial indices
            if n_attn_check > 0:
                attn_idx = set(rng.choice(T, size=n_attn_check, replace=False))
            else:
                attn_idx = set()

            n_needed = (T - n_attn_check) * n_shown + n_attn_check * (n_shown - 1)
            if pool_size != n_needed:
                raise ValueError(
                    f"(s={s}, p={p}) has {pool_size} observed images, "
                    f"but expected {n_needed} to run {T} trials with {n_attn_check} attention-check trials."
                )

            perm = rng.permutation(pool)
            cursor = 0

            for t in range(T):
                k = (n_shown - 1) if t in attn_idx else n_shown
                ids = perm[cursor:cursor + k]
                cursor += k

                vals = latent[s, p, ids]
                if np.isnan(vals).any():
                    raise ValueError(f"NaN encountered in shown items at (s={s}, p={p}, t={t}).")

                # update shown counts
                shown_counts[s, p, ids] += 1

                # deterministic selection (top n_select by vals, tie -> lower id)
                order = np.lexsort((ids, -vals))
                sel = ids[order[:n_select]]
                selected_counts[s, p, sel] += 1

    expected_selected = T * n_select
    assert np.all(selected_counts.sum(axis=-1) == expected_selected), "selected totals mismatch."
    assert np.all(shown_counts.sum(axis=-1) == n_needed), "shown totals mismatch."
    assert np.all(selected_counts <= shown_counts), "selected_counts should be <= shown_counts."

    return selected_counts, shown_counts

def count_to_score(
    selected_counts: np.ndarray,
    shown_counts: np.ndarray,
) -> np.ndarray:
    """
    Compute scores from counts.

    Args:
        selected_counts: (S,P,I) counts of how many times each image was selected
        shown_counts:    (S,P,I) counts of how many times each image was shown

    Returns:
        score: (S, I) float scores in [0,1], NaN where shown_counts == 0
    """
    selected_counts = selected_counts.sum(axis=1)  # (S, I)
    shown_counts = shown_counts.sum(axis=1)  # (S, I)
    score = np.divide(
        selected_counts,
        shown_counts,
        out=np.full(selected_counts.shape, np.nan, dtype=float),
        where=shown_counts > 0,
    )  # (S, I)
    return score

def corr_per_sim(score: np.ndarray, img_mu: np.ndarray) -> np.ndarray:
    """
    score: (S, I) float, may contain NaN
    img_mu: (S, I) ground-truth utilities, one world per simulation
    returns: (S,) correlations (NaN if not computable)
    """
    S, I = score.shape
    out = np.full(S, np.nan, dtype=float)

    for s in range(S):
        x = score[s]
        mask = ~np.isnan(x)
        if mask.sum() < 2:
            continue
        # pearsonr also fails if x or y is constant over masked entries
        xs = x[mask]
        ys = img_mu[s][mask]
        if np.all(xs == xs[0]) or np.all(ys == ys[0]):
            continue
        out[s] = pearsonr(xs, ys)[0]
    return out
