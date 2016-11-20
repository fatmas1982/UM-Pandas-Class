import numpy as np
import pandas as pd
from scipy.stats import ttest_ind


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 
          'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 
          'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 
          'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 
          'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 
          'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 
          'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 
          'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 
          'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 
          'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 
          'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 
          'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 
          'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 
          'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 
          'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 
          'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 
          'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 
          'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 
          'VA': 'Virginia'}
          
def get_list_of_university_towns():
    '''
    
    Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. 
    
    The format of the DataFrame should be:
    DataFrame( [ ["Michigan","Ann Arbor"], ["Michigan", "Yipsilanti"] ], columns=["State","RegionName"]  )
    
    '''
    
    def getST(State):
        return list(states.keys())[list(states.values()).index(State)]
    
    cols_to_keep = ['State', 'RegionName']
    uni_towns = pd.read_table("university_towns.txt", header = None)
    uni_towns['StateInd'] = uni_towns[0].apply(lambda x: x[-6:] == "[edit]")
    uni_towns['State'] = np.where(uni_towns['StateInd'], uni_towns[0], np.nan)
    uni_towns['State'] = uni_towns['State'].ffill()
    uni_towns['State'] = uni_towns['State'].map(lambda x: str(x)[:-6])
    uni_towns['ST'] = uni_towns['State'].apply(lambda x: getST(x))
    uni_towns['RegionName'] = uni_towns[0].apply(lambda x: str(x).split('(')[0].strip())
    uni_towns = uni_towns[uni_towns['StateInd']==False][cols_to_keep]
    uni_towns = uni_towns.reset_index()
    return uni_towns[cols_to_keep]

#get_list_of_university_towns()


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    # read the gdplev.xls file
    # locate 2 quarters of gdp decline
    # column e,g, rows 221 on down
    gdpfile = pd.ExcelFile('gdplev.xls')
    gdp = gdpfile.parse('Sheet1', skiprows = 219, parse_cols = [4, 6], names = ['Quarter', 'GDP'])
    gdp['GDPDiff'] = gdp['GDP'].diff()
    gdp = gdp.reset_index()
    gdp = gdp[gdp['GDPDiff']<0]
    gdp['IndexDiff'] = gdp['index'].diff()
    gdp2 = gdp[gdp['IndexDiff'] == 1].head(1)
    i = gdp2['index']
    return str(gdp.ix[(i-1)]['Quarter']).split()[1]

#get_recession_start()


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    # read the gdplev.xls file
    # locate 2 quarters of gdp growth
    # column e,g, rows 221 on down
    gdpfile = pd.ExcelFile('gdplev.xls')
    gdp = gdpfile.parse('Sheet1', skiprows = 219, parse_cols = [4, 6], names = ['Quarter', 'GDP'])
    gdp['GDPDiff'] = gdp['GDP'].diff()
    gdp = gdp.reset_index().tail(65-34)
    gdp = gdp[gdp['GDPDiff']>0]
    gdp['IndexDiff'] = gdp['index'].diff()
    
    gdp2 = gdp[gdp['IndexDiff'] == 1].head(1)
    i = gdp2['index']
    return str(gdp.ix[i]['Quarter']).split()[1]       

#get_recession_end()


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    # read the gdplev.xls file
    # s the quarter within a recession which had the lowest GDP.
    # column e,g, rows 221 on down
    gdpfile = pd.ExcelFile('gdplev.xls')
    gdp = gdpfile.parse('Sheet1', skiprows = 219, parse_cols = [4, 6], names = ['Quarter', 'GDP'])
    gdp['GDPDiff'] = gdp['GDP'].diff()
    gdp = gdp.reset_index().tail(65-34).head(5).sort_values('GDP').head(1)      
    return str(gdp['Quarter']).split()[1]

#get_recession_bottom()


def convert_housing_data_to_quarters():
    '''
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    #1,2,51-250
    z = pd.read_csv("City_Zhvi_AllHomes.csv")
    z['State'] = z['State'].map(lambda x: states[x])
    #list of month column names
    col_keep = ['{}-{num:02d}'.format(x,num=y) 
            for x in range(2000,2017) 
            for y in range(1,13) 
            if not(x==2016 and y>8)]
    
    
    #Dict for month-to-quarter lookup
    Quarters = { x:'{}q{}'.format(x.split('-')[0],y) 
             for x in col_keep 
             for y in range(1,5) 
             if -(-int(x.split('-')[1])//3)==y
           } 
    z2 = z[col_keep]
    z2=z2.T
    z2['Month'] = z2.index
    z2['Quarter'] = z2['Month'].map(lambda x: Quarters[x])
    z2=z2.reset_index()
    z2=z2.groupby('Quarter').mean().T
    z3=pd.concat([z[['RegionName', 'State']],z2], axis=1).set_index(['State','RegionName'])
    return z3

#convert_housing_data_to_quarters()




def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    #recession = ['2008q3', '2008q4', '2009q1', '2009q2']
    Keepers = [ 'Delta']
    #col_keep = ['test']
    
    a = convert_housing_data_to_quarters()
    #a['test']=get_list_of_university_towns()
    b = get_list_of_university_towns()
    b['Type'] = "university town"
    b=b.set_index(['State','RegionName'])
    c = a.merge(b, left_index=True, right_index=True, how='left')
    c['Type'].fillna("non-university town", inplace=True)
    c['Delta'] = c[get_recession_bottom()] - c[get_recession_start()]
    
    #return a.head()[col_keep]
    
    uni = c[c['Type'] == "university town"][Keepers]
    nuni = c[c['Type'] == "non-university town"][Keepers]
    
    t,p = ttest_ind(uni, nuni, equal_var = False, nan_policy = 'omit')
    
    if (p<.01): 
        bDiff=True
    else:
        bDiff = False
    
    if (t>0):
        better = "university town"
    else:
        better = "non-university town"
        
    #("ttest_ind:            t = %g  p = %g" % (t, p))    
        
    return (bDiff, float(p), better)
                    
#run_ttest()
print(get_list_of_university_towns())
print(run_ttest())


#Ttest_indResult(statistic=masked_array(data = [4.046100486758151],
#             mask = [False],
#       fill_value = 1e+20)
#, pvalue=masked_array(data = 6.702922213085478e-05,
#             mask = False,
#       fill_value = 1e+20)
#)