import pandas as pd
from itertools import product

## Set basic check functions to simplify constraints later
def soil_moisture_all_same(row):
    if (row['alt1.SM_A'] == row['alt2.SM_A'] and row['alt1.SM_F'] == row['alt2.SM_F'] and row['alt1.SM_C'] == row['alt2.SM_C']):
        return True
    return False

def soil_nutrition_all_same(row):
    if (row['alt1.SN_A'] == row['alt2.SN_A'] and row['alt1.SN_F'] == row['alt2.SN_F'] and row['alt1.SN_C'] == row['alt2.SN_C']):
        return True
    return False

def weather_all_same(row):
    if (row['alt1.W_A'] == row['alt2.W_A']):
        return True
    return False

def climate_all_same(row):
    if (row['alt1.C_A'] == row['alt2.C_A']):
        return True
    return False

## Define a function to check if an alternative meets the constraints - this is for singular alternatives
# It filters the possible alternatives based on basic constraints before constructing the choice sets (multiple alts)
# This reduces iteration overhead
def valid_alternative(row):
    # Check if the row meets the constraints.

    #set check value
    check = True

    # Soil moisture attributes are all zero when any one is zero
    if row['SM_A'] == 0 or row['SM_F'] == 1 or row['SM_C'] == 1:
       if not (row['SM_C'] == 1 and row['SM_F'] == 1 and row['SM_A'] == 0):
          check = False

    # Soil nutrition attributes are all zero when any one is zero
    if row['SN_A'] == 0 or row['SN_F'] == 1 or row['SN_C'] == 1:
       if not (row['SN_C'] == 1 and row['SN_F'] == 1 and row['SN_A'] == 0):
          check = False

    return check

## Define a function to check if a choice set meets the constraints
# This function checks if a choice set (with two alternatives) meets the constraints
def valid_choice(row):
    # set check value
    check = True

    # set at least one attribute to overlap in each alternative
    if not (
        weather_all_same(row) or
        climate_all_same(row) or
        soil_moisture_all_same(row) or
        soil_nutrition_all_same(row)
    ):
        check = False

  # use the above to further constraint so at least two attributes must be overlapping (not including cost)
    if weather_all_same(row):
        if not(
            climate_all_same(row) or
            soil_moisture_all_same(row) or
            soil_nutrition_all_same(row)
        ):
            check = False
    if climate_all_same(row):
        if not(
            weather_all_same(row) or
            soil_moisture_all_same(row) or
            soil_nutrition_all_same(row)
        ):
            check = False
    if soil_moisture_all_same(row):
        if not(
            weather_all_same(row) or
            climate_all_same(row) or
            soil_nutrition_all_same(row)
        ):
            check = False
    if soil_nutrition_all_same(row):
        if not(
            weather_all_same(row) or
            climate_all_same(row) or
            soil_moisture_all_same(row)
        ):
            check = False

    # ensure only at most two attributes are set to the same level in each alternative
    if (weather_all_same(row) and climate_all_same(row)):
        if soil_moisture_all_same(row) or soil_nutrition_all_same(row):
            check = False
    if (weather_all_same(row) and soil_moisture_all_same(row)):
        if climate_all_same(row) or soil_nutrition_all_same(row):
            check = False
    if (weather_all_same(row) and soil_nutrition_all_same(row)):
        if climate_all_same(row) or soil_moisture_all_same(row):
            check = False
    if (climate_all_same(row) and soil_moisture_all_same(row)):
        if weather_all_same(row) or soil_nutrition_all_same(row):
            check = False
    if (climate_all_same(row) and soil_nutrition_all_same(row)):
        if weather_all_same(row) or soil_moisture_all_same(row):
            check = False
    if (soil_moisture_all_same(row) and soil_nutrition_all_same(row)):
        if weather_all_same(row) or climate_all_same(row):
            check = False

    # enforce dominance - if all information attributes in one alternative are greater than the other, cost should also be higher
    if (row['alt1.W_A'] >= row['alt2.W_A'] and
        row['alt1.C_A'] >= row['alt2.C_A'] and
        row['alt1.SM_A'] >= row['alt2.SM_A'] and
        row['alt1.SM_F'] >= row['alt2.SM_F'] and
        row['alt1.SM_C'] >= row['alt2.SM_C'] and
        row['alt1.SN_A'] >= row['alt2.SN_A'] and
        row['alt1.SN_F'] >= row['alt2.SN_F'] and
        row['alt1.SN_C'] >= row['alt2.SN_C']
        ):
        if not (row['alt1.C'] > row['alt2.C']):
            check = False
    if (row['alt1.W_A'] <= row['alt2.W_A'] and
        row['alt1.C_A'] <= row['alt2.C_A'] and
        row['alt1.SM_A'] <= row['alt2.SM_A'] and
        row['alt1.SM_F'] <= row['alt2.SM_F'] and
        row['alt1.SM_C'] <= row['alt2.SM_C'] and
        row['alt1.SN_A'] <= row['alt2.SN_A'] and
        row['alt1.SN_F'] <= row['alt2.SN_F'] and
        row['alt1.SN_C'] <= row['alt2.SN_C']
        ):
        if not (row['alt1.C'] < row['alt2.C']):
            check = False

    return check


## 1. Define Attributes and Levels
attributes = {
    'W_A': [10,30,50,80],
    'C_A': [10,30,50,80],
    'SM_A': [0,10,30,50,80],
    'SM_F': [1,2,3],
    'SM_C': [1,2,3],
    'SN_A': [0, 10,30,50,80],
    'SN_F': [1,2,3],
    'SN_C': [1,2,3],
    'C' : [50, 250, 1250, 3500]
}


## 2. Generate All Combinations
# Get all combinations of attribute levels
levels_product = list(product(*attributes.values()))

# Create a list of dictionaries of basic alternatives for DataFrame integrating alternative-level constraints
design_data = []
for combo in levels_product:
    row = dict(zip(attributes.keys(), combo))

    #check if row meets the constraints
    if valid_alternative(row):
        # if True, append to design_data
        design_data.append(row)


## 3. Structure the Design Matrix
df_design = pd.DataFrame(design_data)


## 4. Construct the choice set matrix integraating multiple alternatives into choices
# loop over combinations of alternatives in df_design, testing if they meet the constraints, if so, append to choice_set_data
# NOTE: this will take some time to run. You should only use this for a strongly restricted design. the example case has ~18,000 alternatives AFTER the valid_alternative function is applied.
# On a single core machine the example given here (a real world partial profiles choice set with complex constraints) will take around 20 minutes to run.
# For larger designs, consider using multiprocessing or other optimization techniques to speed up the process.
choice_set_data = []
for i in range(len(df_design)):
    for j in range(i + 1, len(df_design)):
        alt1 = df_design.iloc[i]
        alt2 = df_design.iloc[j]

        # Create a row for the choice set
        choice_set_row = {
            'alt1.W_A': alt1['W_A'],
            'alt1.C_A': alt1['C_A'],
            'alt1.SM_A': alt1['SM_A'],
            'alt1.SM_F': alt1['SM_F'],
            'alt1.SM_C': alt1['SM_C'],
            'alt1.SN_A': alt1['SN_A'],
            'alt1.SN_F': alt1['SN_F'],
            'alt1.SN_C': alt1['SN_C'],
            'alt1.C': alt1['C'],
            'alt2.W_A': alt2['W_A'],
            'alt2.C_A': alt2['C_A'],
            'alt2.SM_A': alt2['SM_A'],
            'alt2.SM_F': alt2['SM_F'],
            'alt2.SM_C': alt2['SM_C'],
            'alt2.SN_A': alt2['SN_A'],
            'alt2.SN_F': alt2['SN_F'],
            'alt2.SN_C': alt2['SN_C'],
            'alt2.C': alt2['C']
        }

        # Check if the choice set meets the constraints
        if valid_choice(choice_set_row):
            choice_set_data.append(choice_set_row)
            # print details of the valid choice set and the total number of valid choice sets found so far
            print(f"Valid choice set found: {choice_set_row}")
            print(f"Total valid choice sets found so far: {len(choice_set_data)}")

## 5 append 'Choice situation' column with integers 1 - len(choice_set_data) as first column of choice_set_data
choice_set_df = pd.DataFrame(choice_set_data)
choice_set_df.insert(0, 'ChoiceSetID', range(1, len(choice_set_df) + 1))

## 6 save to target directory as .csv file without row index
target_wd = 'C:/Users/User/Coding/cropping-information-choice-experiment-design-python/'
file_name = 'partial_profiles_candidates_with_all_conditions_met.csv'
choice_set_df.to_csv(target_wd + file_name, index=False)
