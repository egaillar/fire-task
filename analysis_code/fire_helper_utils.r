################ load packages ################

library(dplyr)
library(tidyverse)

######################## FOR DATA CLEANING ########################

######################## filter qualtrics data collected via prolific ########################

preproc_prolific <- function (prolific_data, qualtrics_data, rating_col_name) {
  
  # extract approved submissions=
  prolific_IDs <- prolific_data  %>% 
    filter(prolific_data$Status == 'APPROVED'|prolific_data$Participant.id == "6647af4ed8f61a601c3a0c87") 
           # this participants had submission issues on prolific end but wrote to us with a completion code, confirming they had finished the study
  
  # make list of approved Prolific IDs
  prolific_IDs <- prolific_IDs$"Participant.id"
  
  # filter qualtrics data for prolific-approved participants
  qualtrics_filtered <- qualtrics_data  %>% 
    filter(PROLIFIC_PID %in% prolific_IDs) %>%
    filter(!is.na(image_rating_results) & browser_check == "pass" & Finished == 1)
  
  qualtrics_final <- qualtrics_filtered %>% 
    dplyr::select(c("StartDate":"RecordedDate","LocationLatitude":"Q4", "browser_check","image_rating_results"))
  
  # rename columns
  old_col_names <- c(colnames(qualtrics_final)) 
  new_col_names <- c("start_date","end_data",	"status",	"ip_address","progress","duration_secs","finished",	"recorded_date","location_lat","location_long","distribution_channel", "language", "browser",	"version", "operating_system",	"resolution",	"ID", "age", "gender", "ethnicity", "browser_check","image_rating_results")
  for(i in 1:29) {
    names(qualtrics_final)[names(qualtrics_final) == old_col_names[i]] = new_col_names[i]
  }
  
  
  qualtrics_final
}


######################## parse strings ########################

parse_ratings <- function(data, column_with_strings) {
  
  full_parsed <- data.frame()
  # iterate over participants
  for (i in 1:nrow(data)) {
    input_string <- data[[column_with_strings]][i]
    formatted_string <- gsub(";", "\n", input_string)
    formatted_string <- gsub(" ", ",", formatted_string)
    result_df <- read.csv(text = formatted_string, stringsAsFactors = FALSE, colClasses = c(click = "character"))
    
    # add participant id
    result_df$participant_id <- data$ID[i]
    full_parsed <- bind_rows(full_parsed, result_df)
  }
  
  return(full_parsed)
}


######################## remove those who failed attention check ########################

remove_attn_fail <- function(data, threshold_val) {
  
  data_filtered <- data %>%
    group_by(participant_id) %>%
    filter(sum(attn_fail == 1) < threshold_val) %>%
    ungroup()
  
}
  

######################## split click columns ########################

split_clicks <- function(data, i) { 
  click_split <- do.call(rbind, strsplit(as.character(data$click), ""))
  colnames(click_split) <- paste0("click_", 1:i)
  split_df <- cbind(data, click_split)
  
  return(split_df)
}


######################## FOR TESTING HYPOTHESIS 1 ########################

######################## define function to calculate mean, sd ########################

calculate_mean_sd <- function(..., method_names = c("Likert", "Slider", "Pair", "Fire")) {
  dfs <- list(...)
  
  #calc stats
  stats <- lapply(dfs, function(df) {
    mean_rt <- mean(df$rt, na.rm = TRUE)
    sd_rt <- sd(df$rt, na.rm = TRUE)
    c(Mean = mean_rt, SD = sd_rt)
  })
  
  #combine to single data frame 
  results <- data.frame(
    Method = method_names,
    Mean = sapply(stats, `[[`, "Mean"),
    SD = sapply(stats, `[[`, "SD")
  )
  
  return(results)
}


######################## remove attention check trials ########################

remove_attn_trials <- function(df, image_cols) {
  df %>%
    filter(!if_any(all_of(image_cols), ~ str_starts(.x, "attn")))
}


######################## run permutation test ########################

permutation_test <- function(data, method1, method2, n_perm = 10000) {
  
  # subset ratings from the two chosen methods
  df_pair <- data %>%
    filter(rating_method %in% c(method1, method2)) %>%
    droplevels() # removes unused factor levels
  
  # calc empirical absolute difference in means
  observed_diff <- abs(mean(df_pair$rt[df_pair$rating_method == method1]) -
                         mean(df_pair$rt[df_pair$rating_method == method2]))
  
  # permutations
  perm_diffs <- replicate(n_perm, {
    shuffled_labels <- sample(df_pair$rating_method)
    abs(mean(df_pair$rt[shuffled_labels == method1]) -
          mean(df_pair$rt[shuffled_labels == method2]))
  })
  
  # p-value
  p_value <- (sum(perm_diffs >= observed_diff) + 1) / (n_perm + 1)
  
  return(list(
    method1 = method1,
    method2 = method2,
    observed_diff = observed_diff,
    p_value = p_value
  ))
}


######################## FOR TESTING HYPOTHESIS 2 ########################

######################## define function to calculate reliability with all participants ########################

split_half_rel_all <- function(data, n_participants) {
  reliability_results <- numeric(10000)
  
  for (i in 1:10000) {
    sampled_participants <- sample(unique(data$participant_id), n_participants)
    sample_data <- filter(data, participant_id %in% sampled_participants)
    
    # split by participant
    pids <- unique(sample_data$participant_id)
    split_assign <- tibble(
      participant_id = pids,
      split = sample(c(1, 2), length(pids), replace = TRUE)
    )
    sample_data <- left_join(sample_data, split_assign, by = "participant_id")
    
    group_1 <- sample_data %>%
      filter(split == 1) %>%
      group_by(image) %>%
      summarise(mean_rating = mean(as.numeric(response), na.rm = TRUE), .groups = "drop")
    group_2 <- sample_data %>%
      filter(split == 2) %>%
      group_by(image) %>%
      summarise(mean_rating = mean(as.numeric(response), na.rm = TRUE), .groups = "drop")
    
    merged <- inner_join(group_1, group_2, by = "image", suffix = c("_1", "_2"))
    
    # require at least 2 complete pairs before cor()
    n_complete <- sum(complete.cases(merged$mean_rating_1, merged$mean_rating_2))
    if (n_complete >= 2) {
      r <- cor(merged$mean_rating_1, merged$mean_rating_2,
                      method = "pearson", use = "complete.obs")
      reliability_results[i] <- 2 * r / (1 + r)
    } else {
      reliability_results[i] <- NA_real_
    }
  }
  
  list(
    mean = mean(reliability_results, na.rm = TRUE),
    sd = sd(reliability_results, na.rm = TRUE),
    results = reliability_results
  )
}


######################## define function to calculate reliability with all participants ########################

n_subset_reliability <- function(data, n_participants) {
  reliability_results <- numeric(10000)
  
  for (i in 1:10000) {
    sampled_participants <- sample(unique(data$participant_id), n_participants)
    sample_data <- filter(data, participant_id %in% sampled_participants)
    
    split <- split(sample_data, sample(rep(1:2, length.out = nrow(sample_data))))
    
    group_1 <- split[[1]] %>%
      group_by(image) %>%
      summarise(mean_rating = mean(as.numeric(response), na.rm = TRUE), .groups = "drop")
    group_2 <- split[[2]] %>%
      group_by(image) %>%
      summarise(mean_rating = mean(as.numeric(response), na.rm = TRUE), .groups = "drop")
    
    merged <- inner_join(group_1, group_2, by = "image", suffix = c("_1", "_2"))
    
    # require ≥ 2 complete pairs before correlating
    n_complete <- sum(complete.cases(merged$mean_rating_1, merged$mean_rating_2))
    if (n_complete >= 2) {
      pearson_corr <- cor(merged$mean_rating_1, merged$mean_rating_2,
                                 method = "pearson", use = "complete.obs")
      reliability_results[i] <- 2 * pearson_corr / (1 + pearson_corr)  # Spearman–Brown
    } else {
      reliability_results[i] <- NA_real_
    }
  }
  
  list(
    mean = mean(reliability_results, na.rm = TRUE),
    sd = sd(reliability_results, na.rm = TRUE)
  )
}


######################## define function to calculate reliability with all participants ########################

n_subset_correlation <- function(data, df_w_mean, n_participants, col_name) {
  corr_values <- numeric(10000)
  for (i in 1:10000) {
    sampled_participants <- sample(unique(data$participant_id), n_participants)
    sample_data <- filter(data, participant_id %in% sampled_participants)
    avg_rating <- sample_data %>% 
      group_by(image) %>% 
      summarise(mean_rating = mean(response, na.rm = TRUE))
    merged <- inner_join(avg_rating, df_w_mean, by = "image")
    # correlate mean ratings from sample with mean across all methods
    corr <- cor(merged$mean_rating, merged[[col_name]], method = "pearson", use = "complete.obs")
    # spearman-brown correction
    corr_values[i] <- 2 * corr / (1 + corr)
  }
  
  # return mean and sd of correlations
  list(mean = mean(corr_values, na.rm = TRUE),
       sd = sd(corr_values, na.rm = TRUE))
}





