# Fast Image Rating Experiment (FIRE)
Data and analysis scripts for the 2025 paper "Reliable and Valid Rating Data in Less Time with the Fast Image Rating Experiment" by [Elizabeth P. Gaillard](https://github.com/egaillar)\*, [Nakwon Rim](https://nwrim.github.io)\*, [Kimberly L. Meidenbauer](https://kim-meidenbauer.github.io/), [Kyoung Whan Choe](https://kywch.github.io), and [Marc G. Berman](https://voices.uchicago.edu/bermanlab/) (* denotes equal contribution).

- Correspondence: Elizabeth Gaillard, egaillard@uchicago.edu
- Last updated: August, 2025
---
This study examined the following rating methods: 

 - Likert scale (**likert**) 
 - sliding scale (**slider**)
 - pairwise comparison (**pair**)
 - Fast Image Rating Experiment (**fire**)
   
   
This study examined the following rating criteria:

 - preference (**pref**)
 - naturalness (**nat**)

Image rating details:

 - Raw image ratings for **likert** and **slider** methods are recorded as numerical values given to each image
 - Raw image ratings for **pair** and **fire** methods are recorded as binary indicators denoting whether each image was selected

# Data
### Raw ###

"raw_data" folder contains raw preference and naturalness ratings by rating method. Image ratings given by each participant are stored in a vector and must be extracted.

 - .csvs are named in the following format: `"[rating
   method]_filtered_[rating criterion].csv"`


### Preprocessed ###

"preprocessed_data" folder contains _post-exclusion_ preference and naturalness ratings with image ratings given by each participant extracted. Files were preprocessed both with and without attention check trials and saved as individual .csvs
       
- .csvs are named in the following format: `"[rating method]_[rating criterion]_preproc_[optional: no attention checks].csv"`
- unless specified in the filename, data include attention check trials


### Reliability ###

"reliability_subsets" folder contains average split half reliability, means, and standard deviations calculated with increasing subsets of participants (N ∈ {100, 110, 120, … 300, 310, 320}) over 10,000 iterations. There is one .csv for each rating method across both rating criteria (preference and naturalness). These files were used for figure creation.

- .csvs are named in the following format: `"rel_sub_[rating method]_[rating criterion]_time_10000_new.csv"`



# Analysis Scripts

**R_scripts_clean** folder contains the following three analysis scripts:

*FIRE_full_clean.Rmd:* preprocessing and primary analyses to be run on raw preference or naturalness .csvs (in raw_data folder). Includes figure creation for rating method efficiency analysis

*FIRE_reliability_figures.Rmd:* figure creation for rating method reliability analysis. To be run on preference and naturalness .csvs in reliability_subsets folder 

*FIRE_validity_figures.Rmd:* figure creation and secondary analyses for rating method validity analysis. To be run on preference and naturalness .csvs in preprocessed_data folder
