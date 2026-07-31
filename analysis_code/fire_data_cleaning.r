################ load packages ################

library(dplyr)
library(tidyverse)
library(readxl)
library(writexl)

################ load helper functions ##################################################################################################
source("fire_helper_utils.R")

################ read files ##################################################################################################

# raw preference data
## from prolific
p_likert_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_likert_pref.csv", colClasses = "character")
p_slider_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_slider_pref.csv", colClasses = "character")
p_pair_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_pair_pref.csv", colClasses = "character")
p_fire_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_fire_pref.csv", colClasses = "character")

## from qualtrics
q_likert_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_likert_pref.csv", colClasses = "character")
q_slider_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_slider_pref.csv", colClasses = "character")
q_pair_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_pair_pref.csv", colClasses = "character")
q_fire_pref <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_fire_pref.csv", colClasses = "character")

# raw naturalness data
## from prolific
p_likert_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_likert_nat.csv", colClasses = "character")
p_slider_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_slider_nat.csv", colClasses = "character")
p_pair_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_pair_nat.csv", colClasses = "character")
p_fire_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/p_fire_nat.csv", colClasses = "character")

## from qualtrics
q_likert_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_likert_nat.csv", colClasses = "character")
q_slider_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_slider_nat.csv", colClasses = "character")
q_pair_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_pair_nat.csv", colClasses = "character")
q_fire_nat <- read.csv("/Users/EPG/Desktop/PhD/repos/fire/raw_data/q_fire_nat.csv", colClasses = "character")


############### filter qualtrics data collected via prolific ##############################################################################

likert_pref <- preproc_prolific(p_likert_pref, q_likert_pref, "image_rating_results")
slider_pref <- preproc_prolific(p_slider_pref, q_slider_pref, "image_rating_results")
pair_pref <- preproc_prolific(p_pair_pref, q_pair_pref, "image_rating_results")
fire_pref <- preproc_prolific(p_fire_pref, q_fire_pref, "image_rating_results")

likert_nat <- preproc_prolific(p_likert_nat, q_likert_nat, "image_rating_results")
slider_nat <- preproc_prolific(p_slider_nat, q_slider_nat, "image_rating_results")
pair_nat <- preproc_prolific(p_pair_nat, q_pair_nat, "image_rating_results")
fire_nat <- preproc_prolific(p_fire_nat, q_fire_nat, "image_rating_results")


############### parse results string for each dataset ##############################################################################

suppressWarnings({
  parsed_likert_pref <- parse_ratings(likert_pref, "image_rating_results")
  parsed_slider_pref <- parse_ratings(slider_pref, "image_rating_results")
  parsed_pair_pref <- parse_ratings(pair_pref, "image_rating_results")
  parsed_fire_pref <- parse_ratings(fire_pref, "image_rating_results")
  
  parsed_likert_nat <- parse_ratings(likert_nat, "image_rating_results")
  parsed_slider_nat <- parse_ratings(slider_nat, "image_rating_results")
  parsed_pair_nat <- parse_ratings(pair_nat, "image_rating_results")
  parsed_fire_nat <- parse_ratings(fire_nat, "image_rating_results")
})

############### filter out those who failed attention check ##############################################################################

parsed_likert_pref <- remove_attn_fail(parsed_likert_pref, 6)
parsed_slider_pref <- remove_attn_fail(parsed_slider_pref, 6)
parsed_pair_pref <- remove_attn_fail(parsed_pair_pref, 3)
parsed_fire_pref <- remove_attn_fail(parsed_fire_pref, 1)

parsed_likert_nat <- remove_attn_fail(parsed_likert_nat, 6)
parsed_slider_nat <- remove_attn_fail(parsed_slider_nat, 6)
parsed_pair_nat <- remove_attn_fail(parsed_pair_nat, 3)
parsed_fire_nat <- remove_attn_fail(parsed_fire_nat, 1)


############### check N for each dataset (should be N = 320 each) ##############################################################################

likert_pref_n <- length(unique(parsed_likert_pref$participant_id))
slider_pref_n <- length(unique(parsed_slider_pref$participant_id))
pair_pref_n <- length(unique(parsed_pair_pref$participant_id))
fire_pref_n <- length(unique(parsed_fire_pref$participant_id))

likert_nat_n <- length(unique(parsed_likert_nat$participant_id))
slider_nat_n <- length(unique(parsed_slider_nat$participant_id))
pair_nat_n <- length(unique(parsed_pair_nat$participant_id))
fire_nat_n <- length(unique(parsed_fire_nat$participant_id))


############### split click columns (only applies to pairwise and fire) #####################################################

split_pair_pref <- split_clicks(parsed_pair_pref, 2)
split_fire_pref <- split_clicks(parsed_fire_pref, 12)

split_pair_nat <- split_clicks(parsed_pair_nat, 2)
split_fire_nat <- split_clicks(parsed_fire_nat, 12)


############### reformat pairwise dataframes #####################################################

image_cols <- split_pair_pref %>%
  select(exp_stage,image11,image12,participant_id)
image_cols$index <- 1:nrow(image_cols)

click_cols <- split_pair_pref %>%
  select(exp_stage,click_1,click_2,participant_id)
click_cols$index <- 1:nrow(click_cols)

parsed_pair_pref_final <- data.frame()
for (i in 1:nrow(image_cols)) {
  for (j in 2:3){
    image_val <- image_cols[i,j]
    click_val <- click_cols[i,j]
    new_row <- data.frame(participant_id = image_cols$participant_id[i],
                          exp_stage = image_cols$exp_stage[i], 
                          image = image_val,
                          position = j-1,
                          response = click_val,
                          stringsAsFactors = FALSE)
    parsed_pair_pref_final <- rbind(parsed_pair_pref_final, new_row)
  }
} 


image_cols <- split_pair_nat %>%
  select(exp_stage,image11,image12,participant_id)
image_cols$index <- 1:nrow(image_cols)

click_cols <- split_pair_nat %>%
  select(exp_stage,click_1,click_2,participant_id)
click_cols$index <- 1:nrow(click_cols)

parsed_pair_nat_final <- data.frame()
for (i in 1:nrow(image_cols)) {
  for (j in 2:3){
    image_val <- image_cols[i,j]
    click_val <- click_cols[i,j]
    new_row <- data.frame(participant_id = image_cols$participant_id[i],
                          exp_stage = image_cols$exp_stage[i], 
                          image = image_val,
                          position = j-1,
                          response = click_val,
                          stringsAsFactors = FALSE)
    parsed_pair_nat_final <- rbind(parsed_pair_nat_final, new_row)
  }
} 


############### reformat fire dataframes #####################################################

image_cols <- split_fire_pref %>%
  dplyr::select(exp_stage,image11:image34,participant_id)
image_cols$index <- 1:nrow(image_cols)

click_cols <- split_fire_pref %>%
  dplyr::select(exp_stage,click_1:click_12,participant_id)
click_cols$index <- 1:nrow(click_cols)

parsed_fire_pref_final <- data.frame()
for (i in 1:nrow(image_cols)) {
  for (j in 2:13){
    image_val <- image_cols[i,j]
    click_val <- click_cols[i,j]
    new_row <- data.frame(participant_id = image_cols$participant_id[i],
                          exp_stage = image_cols$exp_stage[i], 
                          image = image_val,
                          position = j-1,
                          response = click_val,
                          stringsAsFactors = FALSE)
    parsed_fire_pref_final <- rbind(parsed_fire_pref_final, new_row)
  }
}


image_cols <- split_fire_nat %>%
  dplyr::select(exp_stage,image11:image34,participant_id)
image_cols$index <- 1:nrow(image_cols)

click_cols <- split_fire_nat %>%
  dplyr::select(exp_stage,click_1:click_12,participant_id)
click_cols$index <- 1:nrow(click_cols)

parsed_fire_nat_final <- data.frame()
for (i in 1:nrow(image_cols)) {
  for (j in 2:13){
    image_val <- image_cols[i,j]
    click_val <- click_cols[i,j]
    new_row <- data.frame(participant_id = image_cols$participant_id[i],
                          exp_stage = image_cols$exp_stage[i], 
                          image = image_val,
                          position = j-1,
                          response = click_val,
                          stringsAsFactors = FALSE)
    parsed_fire_nat_final <- rbind(parsed_fire_nat_final, new_row)
  }
}
############### remove attention check images #####################################################

parsed_likert_pref_final <- parsed_likert_pref %>% filter(!str_starts(image, "attn"))
parsed_slider_pref_final <- parsed_slider_pref %>% filter(!str_starts(image, "attn"))
parsed_pair_pref_final <- parsed_pair_pref_final %>% filter(!str_starts(image, "attn"))
parsed_fire_pref_final <- parsed_fire_pref_final %>% filter(!str_starts(image, "attn"))

parsed_likert_nat_final <- parsed_likert_nat %>% filter(!str_starts(image, "attn"))
parsed_slider_nat_final <- parsed_slider_nat %>% filter(!str_starts(image, "attn"))
parsed_pair_nat_final <- parsed_pair_nat_final %>% filter(!str_starts(image, "attn"))
parsed_fire_nat_final <- parsed_fire_nat_final %>% filter(!str_starts(image, "attn"))
