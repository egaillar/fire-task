# Fast Image Rating Experiment (FIRE)
Data and analysis scripts for the 2025 paper "Reliable and Valid Rating Data in Less Time with the Fast Image Rating Experiment" by [Elizabeth P. Gaillard](https://github.com/egaillar)\*, [Nakwon Rim](https://nwrim.github.io)\*, [Kimberly L. Meidenbauer](https://kim-meidenbauer.github.io/), [Kyoung Whan Choe](https://kywch.github.io), and [Marc G. Berman](https://voices.uchicago.edu/bermanlab/) (* denotes equal contribution).

# Data
**raw_data** folder contains raw preference and naturalness ratings by rating method (Likert scale, sliding scale, pairwise comparison, or Fast Image Rating Experiment (FIRE))


**preprocessed_data** folder contains post-exclusion preference and naturalness ratings with image scores given by each participant extracted. Files were preprocessed both with and without attention check trials and saved as individual .csvs 
       
*Image score for Likert and sliding scale methods:* numerical rating given to each image
       
*Image score for pairwise and FIRE methods:* binary rating indicating that each image was either selected or unselected

        
**reliability_subsets** folder contains average split half reliability, means, and standard deviations calculated with increasing subsets of participants (N ∈ {100, 110, 120, … 300, 310, 320}) over 10,000 iterations. There is one .csv for each rating method across both rating criteria (preference and naturalness)

# Analysis Scripts

**R_script_clean** folder contains the following three analysis scripts:

*FIRE_full_clean.Rmd:* preprocessing and primary analyses to be run on raw preference or naturalness .csvs (in raw_data folder). Includes figure creation for rating method efficiency analysis

*FIRE_reliability_figures.Rmd:* figure creation for rating method reliability analysis. To be run on preference and naturalness .csvs in reliability_subsets folder 

*FIRE_validity_figures.Rmd:* figure creation and secondary analyses for rating method validity analysis. To be run on preference and naturalness .csvs in preprocessed_data folder
