from pathlib import Path
import numpy as np
import pandas as pd
from numpy.random import default_rng
from tqdm import tqdm

from helpers import simulate_world, latent_to_ratings, latent_to_count, corr_per_sim, count_to_score

SEED = 0
N_I = 1104
N_P_MIN = 50
N_P_MAX = 160
N_SIMULATIONS = 10000
N_JUDGED_PER_PERCEIVER = 106

MU_DIST = 'normal'
MU_MEAN = 0.6621166787688665
MU_SD = 0.7080305928859372
NOISE_SD = 1.410667812424766

LIKERT_CUTPOINTS = np.array([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5], dtype=float) # 1-7
SLIDER_CUTPOINTS = np.linspace(-3.0, 3.0, num=100, dtype=float) # 0-100
PAIRWISE_PARAMETERS = {
    'n_trials': N_JUDGED_PER_PERCEIVER // 2, 'n_shown': 2, 'n_select': 1,
    'n_attn_check': 0
}
FIRE_PARAMETERS = {
    'n_trials': 9, 'n_shown': 12, 'n_select': 4, 'n_attn_check': 2
}

OUT_PATH = Path('outputs/simulations/preference_parameters.csv')
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    rng = default_rng(SEED)

    n_perceivers_list = list(range(N_P_MAX, N_P_MIN - 1, -5))

    result_matrix = np.full((len(n_perceivers_list), N_SIMULATIONS, 4), np.nan)

    for i, n_perceivers in tqdm(enumerate(n_perceivers_list), total=len(n_perceivers_list)):
        img_mu, latent = simulate_world(
            n_images=N_I,
            n_perceivers=n_perceivers,
            n_simulations=N_SIMULATIONS,
            n_judged_per_perceiver=N_JUDGED_PER_PERCEIVER,
            mu_dist=MU_DIST,
            mu_mean=MU_MEAN,
            mu_sd=MU_SD,
            noise_sd=NOISE_SD,
            rng=rng,
        ) # img_mu, latent: (n_images,), (S, P, I)

        # likert
        likert = latent_to_ratings(latent, cutpoints=LIKERT_CUTPOINTS)
        likert_score = np.nanmean(likert, axis=1) + 1 # adding 1 to make 1-7 scale
        result_matrix[i, :, 0] = corr_per_sim(likert_score, img_mu)
        del likert, likert_score

        # slider
        slider = latent_to_ratings(latent, cutpoints=SLIDER_CUTPOINTS)
        slider_score = np.nanmean(slider, axis=1)
        result_matrix[i, :, 1] = corr_per_sim(slider_score, img_mu)
        del slider, slider_score
        
        # pairwise
        p_select, p_shown = latent_to_count(latent, rng=rng, **PAIRWISE_PARAMETERS)
        pairwise_score = count_to_score(p_select, p_shown)
        result_matrix[i, :, 2] = corr_per_sim(pairwise_score, img_mu)
        del p_select, p_shown, pairwise_score

        # fire
        f_select, f_shown = latent_to_count(latent, rng=rng, **FIRE_PARAMETERS)
        fire_score = count_to_score(f_select, f_shown)
        result_matrix[i, :, 3] = corr_per_sim(fire_score, img_mu)
        del f_select, f_shown, fire_score

    # save results as dataframe
    records = []
    for i, n_perceivers in enumerate(n_perceivers_list):
        for s in range(N_SIMULATIONS):
            for m in range(4):
                records.append({
                    'n_perceivers': n_perceivers,
                    'simulation': s,
                    'method': ['likert', 'slider', 'pairwise', 'fire'][m],
                    'correlation': result_matrix[i, s, m],
                })

    df_results = pd.DataFrame.from_records(records)

    df_results.to_csv(OUT_PATH, index=False)