## convert a design from the mod fed algorithm to the ngene format for evaluation
import pandas as pd

## Format needs to be as follows:
# 1. first column is labelled 'choice situation' and is numbered from 1 to K choices
# 2. rows represent choice situations with columns labelled 'alt_name.att_name'
# 3. effects should not be in different columns but rather labelled as different integers under the overall attribute name (e.g. 'alt1.SM_F', not 'alt.SM_F1' + 'alt.SM_F2' + ...)
# 4. remove any reference to the no choice option - this is algorithmically added in ngene

def ngene_attribute_colnames():
    attributes = [
        'W_A', 'C_A', 'SM_A', 'SM_F', 'SM_C',
        'SN_A', 'SN_F', 'SN_C', 'C'
    ]

    return attributes.lower()

def convert_des_to_ngene_format():
    # read in latest design
    design = pd.read_csv('latest_design.csv')

    # Design colnames
    #['no.choice.cte', 'wa', 'ca', 'sma', 'smfq', 'smfd', 'smcr', 'smcc',
    #   'sna', 'snfm', 'snfd', 'sncl', 'sncc', 'cost']

    # remove all rows where the no.choice.cte column is equal to 1
    design = design[design['no.choice.cte'] != 1]

    # reset design index to start from 0 and increment by 1
    design.reset_index(drop=True, inplace=True)

    # reset the no.choice.cte column to hold repeating 1 and 2 values indicating alternatives 1 and 2 respectively
    design['no.choice.cte'] = design.index % 2 + 1

    # split the design into two dataframes, one for each alternative based on the no.choice.cte column
    alt1 = design[design['no.choice.cte'] == 1].copy()
    alt2 = design[design['no.choice.cte'] == 2].copy()

    # drop the no.choice.cte column from both dataframes
    alt1.drop(columns=['no.choice.cte'], inplace=True)
    alt2.drop(columns=['no.choice.cte'], inplace=True)

    # Merge the effects columns (starting with 'smf', 'smc', 'snf' and 'snc') to match [0,1,2] with mapping as follows:
    # smfq = 0 and smfd = 0, then SM_F = 0
    # smfq = 1 and smfd = 0, then SM_F = 1
    # smfq = 0 and smfd = 1, then SM_F = 2

    # smcr = 0 and smcc = 0, then SM_C = 0
    # smcr = 1 and smcc = 0, then SM_C = 1
    # smcr = 0 and smcc = 1, then SM_C = 2

    # snfm = 0 and snfd = 0, then SN_F = 0
    # snfm = 1 and snfd = 0, then SN_F = 1
    # snfm = 0 and snfd = 1, then SN_F = 2

    # sncl = 0 and sncc = 0, then SN_C = 0
    # sncl = 1 and sncc = 0, then SN_C = 1
    # sncl = 0 and sncc = 1, then SN_C = 2

    # create new vars with updated naming for the effects attributes
    alt1['SM_F'] = 0
    alt1.loc[(alt1['smfq'] == 1) & (alt1['smfd'] == 0), 'SM_F'] = 1
    alt1.loc[(alt1['smfq'] == 0) & (alt1['smfd'] == 1), 'SM_F'] = 2
    alt1['SM_C'] = 0
    alt1.loc[(alt1['smcr'] == 1) & (alt1['smcc'] == 0), 'SM_C'] = 1
    alt1.loc[(alt1['smcr'] == 0) & (alt1['smcc'] == 1), 'SM_C'] = 2
    alt1['SN_F'] = 0
    alt1.loc[(alt1['snfm'] == 1) & (alt1['snfd'] == 0), 'SN_F'] = 1
    alt1.loc[(alt1['snfm'] == 0) & (alt1['snfd'] == 1), 'SN_F'] = 2
    alt1['SN_C'] = 0
    alt1.loc[(alt1['sncl'] == 1) & (alt1['sncc'] == 0), 'SN_C'] = 1
    alt1.loc[(alt1['sncl'] == 0) & (alt1['sncc'] == 1), 'SN_C'] = 2
    alt2['SM_F'] = 0
    alt2.loc[(alt2['smfq'] == 1) & (alt2['smfd'] == 0), 'SM_F'] = 1
    alt2.loc[(alt2['smfq'] == 0) & (alt2['smfd'] == 1), 'SM_F'] = 2
    alt2['SM_C'] = 0
    alt2.loc[(alt2['smcr'] == 1) & (alt2['smcc'] == 0), 'SM_C'] = 1
    alt2.loc[(alt2['smcr'] == 0) & (alt2['smcc'] == 1), 'SM_C'] = 2
    alt2['SN_F'] = 0
    alt2.loc[(alt2['snfm'] == 1) & (alt2['snfd'] == 0), 'SN_F'] = 1
    alt2.loc[(alt2['snfm'] == 0) & (alt2['snfd'] == 1), 'SN_F'] = 2
    alt2['SN_C'] = 0
    alt2.loc[(alt2['sncl'] == 1) & (alt2['sncc'] == 0), 'SN_C'] = 1
    alt2.loc[(alt2['sncl'] == 0) & (alt2['sncc'] == 1), 'SN_C'] = 2

    # remove the original columns that were used to create the effects
    alt1.drop(columns=['smfq', 'smfd', 'smcr', 'smcc', 'snfm', 'snfd', 'sncl', 'sncc'], inplace=True)
    alt2.drop(columns=['smfq', 'smfd', 'smcr', 'smcc', 'snfm', 'snfd', 'sncl', 'sncc'], inplace=True)

    # append 'alt1' and 'alt2' to the column names of the respective dataframes
    alt1.columns = [f'alt1.{col}' for col in alt1.columns]
    alt2.columns = [f'alt2.{col}' for col in alt2.columns]

    # bind the two dataframes by columns
    ngene_format = pd.concat([alt1, alt2], axis=1)

    # set all colnames to lower case
    ngene_format.columns = [col.lower() for col in ngene_format.columns]

    # create a new column 'choice situation' that is numbered from 1 to K choices
    ngene_format.insert(0, 'choice situation', range(1, len(ngene_format) + 1))

    # print rows of the new dataframe to console
    print(f'created ngene format design with {len(ngene_format)} rows (choice situations)')

    # save the new dataframe to a csv file
    save_path = 'ngene_format_latest_design.csv'
    ngene_format.to_csv(save_path, index=False)

    return ngene_format
