## Uses the candidate set generated in python to operationalise a modified federove choice experimetn design algorithm

require('idefix')
require('here')

# load target design
candidates <- read.csv(paste(here(),"//data//partial_profiles_candidates_with_all_conditions_met_long.csv", sep=""))
#candidates <- read.csv(paste(here(),"//data//partial_profiles_candidates_with_additional_conditions_met_long.csv", sep=""))

# add in CTE column
cte = rep(c(0,0,1), nrow(candidates)/3)
candidates_with_cte <- cbind(cte, candidates)
colnames(candidates_with_cte) <- c('nochoice.cte', colnames(candidates))

alts = rep(c(1,2,0), nrow(candidates)/3) # create alternative index

# We need to expand out the columns to account for the effects coding of the effects attributes
soil_moisture_frequency_quarterly = 1*(candidates_with_cte$SM_F == 1)
soil_moisture_frequency_daily = 1*(candidates_with_cte$SM_F == 2)
soil_nutrition_frequency_monthly = 1*(candidates_with_cte$SN_F == 1)
soil_nutrition_frequency_daily = 1*(candidates_with_cte$SN_F == 2)
soil_moisture_coverage_regional = 1*(candidates_with_cte$SM_C == 1)
soil_moisture_coverage_continuous = 1*(candidates_with_cte$SM_C == 2)
soil_nutrition_coverage_low = 1*(candidates_with_cte$SN_C == 1)
soil_nutrition_coverage_continuous = 1*(candidates_with_cte$SN_C == 2)

# now expand out columns for alternatives
candidates_with_cte$W_A1 = candidates_with_cte$W_A * (alts==1)
candidates_with_cte$W_A2 = candidates_with_cte$W_A * (alts==2)
candidates_with_cte$C_A1 = candidates_with_cte$C_A * (alts==1)
candidates_with_cte$C_A2 = candidates_with_cte$C_A * (alts==2)
candidates_with_cte$SM_A1 = candidates_with_cte$SM_A * (alts==1)
candidates_with_cte$SM_A2 = candidates_with_cte$SM_A * (alts==2)
candidates_with_cte$SM_F_QUARTERLY1 = soil_moisture_frequency_quarterly * (alts==1)
candidates_with_cte$SM_F_QUARTERLY2 = soil_moisture_frequency_quarterly * (alts==2)
candidates_with_cte$SM_F_DAILY1 = soil_moisture_frequency_daily * (alts==1)
candidates_with_cte$SM_F_DAILY2 = soil_moisture_frequency_daily * (alts==2)
candidates_with_cte$SN_A1 = candidates_with_cte$SN_A * (alts==1)
candidates_with_cte$SN_A2 = candidates_with_cte$SN_A * (alts==2)
candidates_with_cte$SM_C_REGIONAL1 = soil_moisture_coverage_regional * (alts==1)
candidates_with_cte$SM_C_REGIONAL2 = soil_moisture_coverage_regional * (alts==2)
candidates_with_cte$SM_C_CONTINUOUS1 = soil_moisture_coverage_continuous * (alts==1)
candidates_with_cte$SM_C_CONTINUOUS2 = soil_moisture_coverage_continuous * (alts==2)

# reform the dataframe
candidates_with_cte_formatted = data.frame(
    "no.choice.cte" = candidates_with_cte$nochoice.cte,
    "wa" = candidates_with_cte$W_A,
    "ca" = candidates_with_cte$C_A,
    "sma" = candidates_with_cte$SM_A,
    "smfq" = soil_moisture_frequency_quarterly,
    "smfd" = soil_moisture_frequency_daily,
    "smcr" = soil_moisture_coverage_regional,
    "smcc" = soil_moisture_coverage_continuous,
    "sna" = candidates_with_cte$SN_A,
    "snfm" = soil_nutrition_frequency_monthly,
    "snfd" = soil_nutrition_frequency_daily,
    "sncl" = soil_nutrition_coverage_low,
    "sncc" = soil_nutrition_coverage_continuous,
    "cost" = candidates_with_cte$C
)
# generate priors

# set draws
n_draws = 25

### set priors
#   use uniform priors (-0.1 to 1) for all attributes except cost - this ensures coverage of zero in the draws

# key parameters
prior_weather = runif(n_draws, min = 0, max = 0.8)
prior_climate = runif(n_draws, min = 0, max = 0.8)
prior_soil_moisture_accuracy = runif(n_draws, min = 0, max = 0.8)
prior_soil_moisture_frequency_quarterly = runif(n_draws, min = 0 , max = 10)
prior_soil_moisture_frequency_daily = runif(n_draws, min = 0 , max = 30)
prior_soil_moisture_coverage_regional = runif(n_draws, min = 0, max = 10)
prior_soil_moisture_coverage_continuous = runif(n_draws, min = 0, max = 30)
prior_soil_nutrition_accuracy = runif(n_draws, min = 0, max = 0.8)
prior_soil_nutrition_frequency_monthly = runif(n_draws, min = 0, max = 10)
prior_soil_nutrition_frequency_daily = runif(n_draws, min = 0, max = 30)
prior_soil_nutrition_coverage_low = runif(n_draws, min = 0, max = 10)
prior_soil_nutrition_coverage_continuous = runif(n_draws, min = 0, max = 30)
prior_cost = runif(n_draws, min = -0.01, max = -0.005)

# no choice CTE
prior_cte = rnorm(n_draws, mean = 0, sd = 5)

priors = cbind(
        prior_weather,
        prior_climate,
        prior_soil_moisture_accuracy,
        prior_soil_moisture_frequency_quarterly,
        prior_soil_moisture_frequency_daily,
        prior_soil_moisture_coverage_regional,
        prior_soil_moisture_coverage_continuous,
        prior_soil_nutrition_accuracy,
        prior_soil_nutrition_frequency_monthly,
        prior_soil_nutrition_frequency_daily,
        prior_soil_nutrition_coverage_low,
        prior_soil_nutrition_coverage_continuous,
        prior_cost = runif(n_draws, min = -1, max = 0)
    )

priors_list = list(
    as.matrix(prior_cte),
    as.matrix(priors)
)

## Generate candidate function
gen_cand = function(all_candidates, nrows, nalts = 3) {
  # sample a subset of candidates
  choice_sets = seq(1,nrow(all_candidates)/nalts)
  choice_set_index = rep(choice_sets, each = nalts) # each choice set has 3 alternatives
  samp = sample(choice_sets, nrows, replace = FALSE)

  new_cand = all_candidates[which(choice_set_index %in% samp),]
  new_cand = as.matrix(new_cand)
  row.names(new_cand) = as.character(1:nrow(new_cand))

  return(new_cand)
}


## Evaluate design function
get_d_eff = function(cand_des, priors_list, n.alts, alt.cte, no.choice = FALSE) {

  d_errors = c()
  for(s in 1:nrow(priors)){
    evdes = EvaluateDesign(
      des = cand_des,
      par.draws = priors_list,
      n.alts = 3, # no choice alternative
      alt.cte = c(0,0,1), # no choice alternative
      no.choice = TRUE
    )

    # collate d errors
    d_errors[s] = evdes$DB.error
    }

    # count NAs
    na_count = sum(is.na(d_errors))
    d_eff = median(1/d_errors[!is.na(d_errors)])

    return(list(
        "deff" = d_eff,
        "na_count" = na_count
    ))
}

check_new_row = function(cand, nalts=3) {
  # generate a new candidate row
  new_row = gen_cand(all_candidates = candidates_with_cte_formatted, nrows = 1)
  current_d_eff = get_d_eff(cand, priors_list, n.alts = 3, alt.cte = c(0,0,1), no.choice = TRUE)$deff

  # loop through all rows and check if replacing any row with cand improves the design
  for (i in 1:(nrow(cand)/nalts)) {
    # replace row i with new_row
    cand_temp = cand
    cand_temp[((i-1)*nalts+1):(i*nalts),] = new_row

    # evaluate the design
    d_eff_temp = get_d_eff(cand_temp, priors_list, n.alts = 3, alt.cte = c(0,0,1), no.choice = TRUE)

    # check na - if na then find another row before continuing
    if (is.na(d_eff_temp$deff)) {
      # check if last row - if so exit
      if (i == (nrow(cand)/nalts)) {
        # if we have checked all rows and not found a better design, return FALSE
        return(list("success" = FALSE, "new_candidate" = NULL))
      }
      # else move to next row
      next
    }

    if (current_d_eff < d_eff_temp$deff) {
      # if the design is better, set success to TRUE and return the new row
      return(list("success" = TRUE, "new_candidate" = cand_temp, "deff" = d_eff_temp$deff))
    } else {
      if (i == (nrow(cand)/nalts)) {
        # if we have checked all rows and not found a better design, return FALSE
        return(list("success" = FALSE, "new_candidate" = NULL))
      }
    }
  }
}


# generate a starting candidate AND CHECK EFF IS NOT NA
cand = gen_cand(candidates_with_cte_formatted, nrows = 48)
d_eff_score = c(get_d_eff(cand, priors_list, n.alts = 3, alt.cte = c(0,0,1), no.choice = TRUE)$deff)


## set design params
end_time = 60*1200 # end time in seconds (6 hours no improvement)
start_time = Sys.time()
running_time = Sys.time() - start_time

# initialise list of candidates
cand_list = list()

# loop
while(running_time < end_time) {

  # sample a new candidate row
  tryCatch({
    cand_check = check_new_row(cand, nalts = 3)
    if (cand_check$success) {
      # a better row was found
      d_eff_score = c(d_eff_score, cand_check$deff)
      cand = cand_check$new_candidate
      start_time = Sys.time() # reset start time
      cand_list = append(cand_list, list(cand))
      print(paste("New candidate found at", Sys.time(), "with D-efficiency:", d_eff_score[length(d_eff_score)]))
      cand_for_saving = as.data.frame(cand)
      # save to .csv
      write.csv(cand_for_saving, paste(here(), "//latest_design_with_additional_cost_constraints.csv", sep=""), row.names = FALSE)
    } else {
      success = FALSE
      print(paste("No better candidate found at", Sys.time(), ". Trying new row..."))
    }
  },
  error = function(e) {
    # if there is an error, print a message and continue
    print(paste("Error in checking new row:", e$message, "Retrying..."))
  })
}

