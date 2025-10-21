library(readr)
library(dplyr)
library(tidyr)
library(stats)
library(purrr)
library(zoo)

# SHAVING OFF EXTRA DATA
conflicts <- read_csv("csv_of_wars.txt")

# Dictionary that will help determine for each country which year we need to search and filter
important_years <- function(conflicts) {
  years_countries <- list()
  
  for (i in 1:nrow(conflicts)) {
    year <- as.integer(conflicts$year_of_start[i])
    years <- seq(year - 10, year, by = 1)  # We want the year of start of war and 10 years before that
    country1 <- conflicts$combatant1[i]
    country2 <- conflicts$combatant2[i]
    
    # Add years to the dictionary for each country
    years_countries[[country1]] <- unique(c(years_countries[[country1]], years))
    years_countries[[country2]] <- unique(c(years_countries[[country2]], years))
  }
  
  return(years_countries)
}

years_countries <- important_years(conflicts)

# This function will help us search for proper variables in World Bank data which has around 1400-1500 variables
study_Data_for_variables <- function() {
  economic_keyword <- c("GDP", "capita", "poverty", "inflation", "unemployment", 
                        "exchange", "interest", "gas", "oil", "energy", "urban", 
                        "rural", "military", "trade")
  demographic_keyword <- c("population", "age", "gender", "religion", "male", "female", 
                           "fertility", "density", "ethnic")
  political_keyword <- c("regime", "war", "majority", "ideology", "territory", "area")
  
  keywords <- c(economic_keyword, demographic_keyword, political_keyword)
  
  # Rows have to be skipped when opening data since CSV starts after 4th row before that it is just messages
  usa_data_path <- file.path("big data", "US.csv")
  usa_study_case <- read_csv(usa_data_path, skip = 4)
  
  # This is where all the 1400+ variables are stored
  total_variables <- usa_study_case$`Indicator Name`
  
  # Finding desirable variables
  matching_variables <- total_variables[grepl(paste(keywords, collapse = "|"), total_variables)]
  
  writeLines(matching_variables, "unfiltered_matching_variables.txt")
  
  return(matching_variables)
}

# Read selected variables manually picked and written in handy_picked_variables.txt
selected_variables <- readLines("handy_picked_variables.txt")

# Filter data frames in big data to only have years 0-10 years before their respective wars, and only variables of interest
filter_country_data <- function(country, path, all_years = FALSE) {
  if (all_years) {
    years_of_interest <- as.character(1960:2023)  # 2023 is max year usually
  } else {
    years_of_interest <- as.character(years_countries[[country]])
  }
  
  data <- read_csv(path, skip = 4)
  
  filtered_data <- data %>%
    filter(`Indicator Name` %in% selected_variables) %>%
    select(c("Indicator Name", years_of_interest)) %>%
    arrange(`Indicator Name`)
  
  return(filtered_data)
}

# Handling missing data
Na_Counter <- function(folder, output_txt) {
  total_cells <- 0
  na_total <- 0
  
  files <- list.files(folder, full.names = TRUE)
  
  for (file in files) {
    data <- read_csv(file)
    na_count <- sum(is.na(data))
    total_count <- nrow(data) * ncol(data)
    
    total_cells <- total_cells + total_count
    na_total <- na_total + na_count
  }
  
  writeLines(sprintf("Total cells: %d\nTotal NAs: %d\nPercentage NAs: %.2f%%", 
                     total_cells, na_total, (na_total / total_cells) * 100), output_txt)
}

# Function to transform and clean data
transpose_and_NA_filter_country <- function(store_folder, input_folder) {
  files <- list.files(input_folder, full.names = TRUE)
  
  for (file in files) {
    data <- read_csv(file)
    
    data_long <- data %>%
      pivot_longer(-`Indicator Name`, names_to = "Years", values_to = "Value") %>%
      spread(`Indicator Name`, Value) %>%
      arrange(Years)
    
    # Interpolation to fill missing values
    data_long <- data_long %>%
      mutate(across(everything(), ~ na.approx(., na.rm = FALSE), .names = "interpolated_{.col}"))
    
    write_csv(data_long, file.path(store_folder, basename(file)))
  }
}

# Function to create war data frames
create_war_data_frame <- function(country_file, year_of_start, folder) {
  path <- file.path(folder, country_file)
  data <- read_csv(path)
  
  valid_years <- as.integer(year_of_start - 10:0)
  data <- data %>%
    filter(Years %in% valid_years) %>%
    mutate(years_before_the_war = year_of_start - as.integer(Years))
  
  return(data)
}

# Function to build OLS model
build_ols_model <- function(final_data_path) {
  final_data <- read_csv(final_data_path)
  
  excluded_vars <- c("Years", "years_before_the_war")
  included_vars <- setdiff(names(final_data), excluded_vars)
  
  y <- final_data$years_before_the_war
  x <- final_data[included_vars]
  
  model <- lm(y ~ ., data = x)
  
  summary(model)
  return(model)
}

# Function to predict war likelihood
War_Predictor_X_Year_CORRECTED <- function(country1, country2, folder) {
  country1_path <- file.path(folder, paste0(country1, ".csv"))
  country2_path <- file.path(folder, paste0(country2, ".csv"))
  
  cntry1 <- read_csv(country1_path)
  cntry2 <- read_csv(country2_path)
  
  model <- build_ols_model("FINAL NA FREE/FINAL_Na_free_dataset.csv")
  coefficients <- coef(model)
  
  pred1 <- sum(cntry1 * coefficients, na.rm = TRUE)
  pred2 <- sum(cntry2 * coefficients, na.rm = TRUE)
  
  final_pred <- (pred1 + pred2) / 2 - 3.7  # Corrected prediction
  return(final_pred)
}

# Test the model
test_the_model <- function(conflicts) {
  results <- list()
  
  for (i in 1:nrow(conflicts)) {
    year <- as.character(conflicts$year_of_start[i])
    country1 <- conflicts$combatant1[i]
    country2 <- conflicts$combatant2[i]
    
    pred <- War_Predictor_X_Year_CORRECTED(country1, country2, "data for predictions")
    
    results[[i]] <- pred
  }
  
  conflicts$Prediction_Accuracy <- unlist(results)
  write_csv(conflicts, "Prediction_accuracy_of_War_Predictor.csv")
}

# Run the model
test_the_model(conflicts)
