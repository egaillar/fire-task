# Fast Image Rating Experiment (FIRE)
Data and analysis scripts for the 2026 paper "Reliable and Valid Rating Data in Less Time with the Fast Image Rating Experiment" by [Elizabeth P. Gaillard](https://github.com/egaillar)\*, [Nakwon Rim](https://nwrim.github.io)\*, [Kimberly L. Meidenbauer](https://kim-meidenbauer.github.io/), [Kyoung Whan Choe](https://kywch.github.io), and [Marc G. Berman](https://voices.uchicago.edu/bermanlab/) (* denotes equal contribution).

- Correspondence: Elizabeth Gaillard, egaillard@uchicago.edu
- Last updated: July, 2026
- Analysis scripts were written by Elizabeth Gaillard, and all analyses were performed in R version 4.2.3. Simulations were written and performed by Nakwon Rim.
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

---
# Data
### Raw ###

"raw_data" folder contains preference and naturalness data which were collected from Qualtrics forms distributed via Prolific. As a result, the folder contains a file downloaded from Qualtrics and a file downloaded from Prolific for each of the rating methods and criterion. 

 - .csvs are named in the following format: `"[p/q]_[rating method]_[rating criterion].csv"`
 - all .csvs are required for analyses

---
# Analysis Scripts

### "fire_analyses_preference.Rmd" ###

Preprocessing and all primary analyses to be run on raw preference data. 

 - data to be analyzed with this script are stored in `"raw_data"` folder

### "fire_analyses_naturalness.Rmd" ###

Preprocessing and all primary analyses to be run on raw naturalness data. 

 - data to be analyzed with this script are stored in `"raw_data"` folder 

### "fire_data_cleaning.R" ###

Data cleaning. To run "fire_analyses_preference.Rmd" or "fire_analyses_naturalness.Rmd", this script must be stored in the same folder.

### "fire_helper_utils.R ###

Helper functions. To run "fire_analyses_preference.Rmd" or "fire_analyses_naturalness.Rmd", this script must be stored in the same folder.




