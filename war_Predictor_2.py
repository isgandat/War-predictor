import numpy as np
import pandas as pn
from pandas import read_csv,DataFrame,isna,concat
from statsmodels.api import OLS,add_constant
import tkinter as tk
import os 
from pathlib import Path


                                #####SHAVING OFF EXTRA DATA##############
conflicts=read_csv("csv_of_wars.txt")
def important_years():
  #dictionary that will help me utilize for which country which year I need to search and filter
   years_countries={}
   for row in conflicts.itertuples(): 
       year=int(row.year_of_start)
       years=set(range(year-10,year+1)) #we want year of start of war and 10 years before that 
       country1=row.combatant1
       country2=row.combatant2
       if country1 in years_countries:
           years_countries[country1]=years_countries[country1].union(years)
       else: #we encounter new country not in dict
           years_countries[country1]=set(years)
       if country2 in years_countries:
           years_countries[country2]=years_countries[country2].union(years)
       else:
           years_countries[country2]=set(years)

   for key,val in years_countries.items():
       years_countries[key]=sorted(list(val))
   return years_countries

years_countries=important_years()


#this functions will help me search for proper varaibles in WB data which has around 1400-1500 variables
def study_Data_for_variables():
   economic_keyword={"GDP","capita","poverty","inflation","unemployment","exchange","interest","gas","oil","energy","urban","rural","military","trade"}
   demographic_keyword={"population","age","gender","religious","religion","male","female","fertility","population density","ethnic"}
   political_keyword={"regime","war","majority","ideology","territory","area"}  
   keywords=economic_keyword.union(demographic_keyword).union(political_keyword) #total keywords that will help me find desirable variables in csvs
   all_matching_variables=set() 
   unfiltered_variables=open("unfiltered_matching_variables.txt","w")
   usa_data_path=os.path.join("big data","US.csv")
   usa_study_case=read_csv(usa_data_path,skiprows=4)  #rows have to be skipped when opening data since csv starts after 4th row before that it is just messages
   total_variables=usa_study_case["Indicator Name"] #this is where all the 1400+ variables are stored
   for variable in total_variables:
       if any(keyword in variable for keyword in keywords):
           all_matching_variables.add(variable)
           unfiltered_variables.write(f"{variable}\n")
   return all_matching_variables

#filtered_vars=study_Data_for_variables()
#print(len(filtered_vars))         Amount of variables after first Big filter was 747 from around 1500
#next I handipicked 15 variables and wrote them in handy_picked_variables.txt
#and wrote them in selected variables
selected_variables=set()
for i in open("handy_picked_variables.txt","r"):
   selected_variables.add(i.strip())





#Based on all the year and variable information we learend l will now filter data frames in big data
#to only have years 0-10 years before their respective wars, and only variables we are interested in

def filter_country_data(country,the_path,all_years=False,skiprows=True,country_name=False):
   if all_years:
       years_of_interest=[str(i) for i in range(1960,2024)] #2023 is max year usually
   else:
       years_of_interest=years_countries.get(country)
       years_of_interest=[str(year) for year in years_of_interest]
   if country_name==False:
       columns_of_interest=["Indicator Name"]+years_of_interest 
   else :
       columns_of_interest=["Indicator Name"]+["Country Name"]+years_of_interest 
    #columns_of_interest is columns we will extract from big dataframe to create data frame that we care about
   if skiprows==True:
       original_data=read_csv(the_path,skiprows=4)
   else:
       original_data=read_csv(the_path)
       filtered_data=original_data[original_data["Indicator Name"].isin(selected_variables)].reset_index(drop=True).copy() #shave off extra vars
       final_data=filtered_data[columns_of_interest].reset_index(drop=True).copy()
       final_data=final_data.sort_values("Indicator Name",ignore_index=True)
       return final_data

def big_data_filtrer():
   for file in os.listdir("big data"):
       the_path=os.path.join("big data",file)
       country=file[:-4] #remove .csv
       filtered_data=filter_country_data(country,the_path)
       the_storage_path=os.path.join("filtered data",file)
       filtered_data.to_csv(the_storage_path,index=False)
   print("all done!")





                                     #NA#
#Now, Data has many Na's which we do not like so let us study Na's, for which years and which variables
                           #Is there most missing data?#
def Na_Counter(country_folder,write_down_txt): 
   tot_cls=0
   Na_s=0
   Na_replacement=0
   Variable_dict={}
   year_dict={}
   country_dict={}
   for country_file in os.listdir(country_folder):
       country=country_file[:-4]
       country_path=os.path.join(country_folder,country_file)
       country_csv=read_csv(country_path)
       for index,row in country_csv.iterrows():
           for col in country_csv.columns:
               tot_cls+=1
               if isna(row[col]):
                   country_dict[country]=country_dict.get(country,0)+1
                   Na_s+=1
                   year_dict[col]=year_dict.get(col,0)+1
                   Variable_dict[row[0]]=Variable_dict.get(row[0],0)+1
   Na_statistics=open(write_down_txt,"w")
   Na_statistics.write("Na staitsitcs\n\n")
   Na_statistics.write("General\n")
   Na_statistics.write(f"total cells: {tot_cls} total Nas: {Na_s} percentage of cell Na's : {Na_s/tot_cls*100} Na replacement rate: {Na_replacement/Na_s*100}\n\n")
   Na_statistics.write("Variables\n")
   for key,val in Variable_dict.items():
       Na_statistics.write(f"{key}:{val}\n")
   Na_statistics.write("Years\n")
   for key,val in year_dict.items():
       Na_statistics.write(f"{key}:{val}\n")
   Na_statistics.write("Countries\n")
   for key,val in country_dict.items():
       Na_statistics.write(f"{key}:{val}\n")
       
   return year_dict,Variable_dict,country_dict  #this will help us find out the Na coverage and effectivness of this method

#Na_years,Na_Variables,Na_countries=Na_Counter("filtered data","Na_statistics.txt")
#we will need this statistic to help us check what is the difference in the NA's after filtering

os.makedirs("Formated and Na filtered",exist_ok=True)
def transpose_and_NA_filter_country(store_folder,folder_country):
   for file_country in os.listdir(folder_country):
       open_path=os.path.join(folder_country,file_country)
       country=read_csv(open_path)
       country.columns = ['Years'] + list(country.columns[1:]) #remove Indicator Name and replace it with years since we are transposing matrix
       #new matrix will have as columns variables and years as the 
       country=country.set_index("Years").T
       country=country.interpolate()
       store_path=os.path.join(store_folder,file_country)
       country.to_csv(store_path,index=False) ##index must be true for transpose matrix when saving it as csv 

#transpose_and_NA_filter_country("Formated and Na filtered","filtered data")

#count new NA's to study the decrease 
def Na_Counter_2(country_folder,write_down_txt): 
   tot_cls=0
   Na_s=0
   Na_replacement=0
   Variable_dict={}
   year_dict={}
   country_dict={}
   for country_file in os.listdir(country_folder):
       country=country_file[:-4]
       country_path=os.path.join(country_folder,country_file)
       country_csv=read_csv(country_path)
       for index,row in country_csv.iterrows():
           for col in country_csv.columns:
               tot_cls+=1
               if isna(row[col]):
                   country_dict[country]=country_dict.get(country,0)+1
                   Na_s+=1
                   year_dict[row[0]]=year_dict.get(row[0],0)+1
                   Variable_dict[col]=Variable_dict.get(col,0)+1
   Na_statistics=open(write_down_txt,"w")
   Na_statistics.write("Na staitsitcs\n\n")
   Na_statistics.write("General\n")
   Na_statistics.write(f"total cells: {tot_cls} total Nas: {Na_s} percentage of cell Na's : {Na_s/tot_cls*100} Na replacement rate: {Na_replacement/Na_s*100}\n\n")
   Na_statistics.write("Variables\n")
   for key,val in Variable_dict.items():
       Na_statistics.write(f"{key}:{val}\n")
   Na_statistics.write("Years\n")
   for key,val in year_dict.items():
       Na_statistics.write(f"{key}:{val}\n")
   Na_statistics.write("Countries\n")
   for key,val in country_dict.items():
       Na_statistics.write(f"{key}:{val}\n")
       
   return year_dict,Variable_dict,country_dict  #this will help us find out the Na coverage and effectivness of this method
#new_Na_years,new_Na_Variables,new_Na_countries=Na_Counter_2("Formated and Na filtered","Na_statistics_postscriptum.txt")
#CPIA gender equality rating (1=low to 6=high):462
#tot.cels=7808 every variable has around 7800/15=520 cells, so most of them are missing for most countries
#Unemployment, male (% of male labor force) (national estimate):324
#Central government debt, total (% of GDP):378 
#Literacy rate, adult total (% of people ages 15 and above):343
#this four variables will be sadly removed because even with interpolate there is more than 50% missing





                         ##Final filtering and joining of datas##
        ############################################################################
def create_war_data_frame(country1_file,year_of_start,country_folder):
   year_of_start=int(year_of_start)
   valid_years=[int(i) for i in range(year_of_start-10,year_of_start+1) if i>=1960]
   country1_path=os.path.join(country_folder,country1_file)
   country1_csv=read_csv(country1_path)
   country1_col_names=["Years"]+list(country1_csv.columns[1:]) #add 2 to differentiate between countries
   country1_csv.columns=country1_col_names
   country1_csv=country1_csv[country1_csv["Years"].isin(valid_years)].copy()
   country1_csv=country1_csv.drop(columns=["Literacy rate, adult total (% of people ages 15 and above)","CPIA gender equality rating (1=low to 6=high)","Central government debt, total (% of GDP)","Unemployment, male (% of male labor force) (national estimate)"])
   years_before_the_war=[(year_of_start-i) for i in list(country1_csv["Years"])]
   country1_csv["years_before_the_war"]=years_before_the_war
   return country1_csv

def create_all_war_dfs(storagefolder,openfolder,wars_csv): #wars is csv that contains information about war
   for row in wars_csv.itertuples():
       thewar=row.war
       if thewar=="Nato_Involvment_in_Kosovo_War":
           continue
       elif thewar=="Soviet-Afghan_War":
           country1="Russia.csv" #closest match to Soviet Union
           country2="Afghanistan.csv"
           year_of_start_=1979
       else:
           country1=f"{row.combatant1}.csv"
           country2=f"{row.combatant2}.csv"
           year_of_start_=row.year_of_start
       x=create_war_data_frame(country1,year_of_start_,openfolder)
       x2=create_war_data_frame(country2,year_of_start_,openfolder)
       store_path=os.path.join(storagefolder,f"{thewar}.csv")
       x.to_csv(store_path,index=False)
       store_path2=os.path.join(storagefolder,f"{thewar} v2.csv")
       x2.to_csv(store_path2,index=False)
   print("all done!")

os.makedirs("war data frames",exist_ok=True)
#create_all_war_dfs("war data frames","Formated and Na filtered",conflicts)

def unify_data_frames(open_folder,store_folder):
   concat_list=[]
   for war_df in os.listdir(open_folder):
      file_path=os.path.join(open_folder,war_df)
      concat_list.append(read_csv(file_path))
   big_df=concat(concat_list,axis=0)
   save_path=os.path.join(store_folder,"Final_unified_data.csv")
   big_df.to_csv(save_path,index=False)
   print("all done")

os.makedirs("unified dataframe for ols",exist_ok=True)
#unify_data_frames("war data frames","unified dataframe for ols")
#let us check Na's for the last time before we remove all Na columns from data set

    #final_Na_years,final_Na_Variables,final_Na_countries=Na_Counter_2("unified dataframe for ols","Na_statistics_finaltxt")##

#there is now only 1400 left from 2700 , however distirbution of the frequency of Nan is different on the variables
#which is probably from the fact that some countries missing values are involved into lots of wars in same years

os.makedirs("FINAL NA FREE",exist_ok=True)
def Na_free_csv():
   unified_save_path=os.path.join("FINAL NA FREE","FINAL_Na_free_dataset.csv")
   unified_read_path=os.path.join("unified dataframe for ols","Final_unified_data.csv")
   Na_free=read_csv(unified_read_path)
   ####!! Energy use has to be sadly dropped because there is no statistics about this variable after 2014-15, this severely
   ####limits both OLS sample size and accurecy of the OLS model!
   Na_free=Na_free.drop(columns=["Energy imports, net (% of energy use)"])
   Na_free=Na_free.dropna(axis=0)
   Na_free=Na_free.set_index("Years")
   Na_free.to_csv(unified_save_path)

#Na_free_csv()





                        ##OLS MODEL AND WAR PREDICTOR FUNCTION##
        ############################################################################

final_data_path=os.path.join("FINAL NA FREE","FINAL_Na_free_dataset.csv")
final_data=read_csv(final_data_path)
excluded_vars=["Years","years_before_the_war","Energy imports, net (% of energy use)"] #exclude dependent variable , and non-numerical variables
####!! Energy use has to be sadly dropped because there is no statistics about this variable after 2014-15, this severely
####limits both OLS sample size and accurecy of the OLS model!
included_vars=final_data.columns.difference(excluded_vars)
y=final_data["years_before_the_war"]
x=final_data[included_vars]
model=OLS(y,x)
results=model.fit() 
#OLS_results=open("OLS_results.txt","w")
#OLS_results.write(str(results.summary()))
#OLS_results.close()
coefficents_from_ols=results.params #this df kind of structure
prediction_dict={}

def prediction_model_maker(input_dict):
   for i in included_vars:
       coef=coefficents_from_ols[i]
       prediction_dict[i]=coef
   prediction=sum(coefficents_from_ols[var]*input_dict[var] for var in input_dict)
   return prediction


##areas to continue in:
##seeing how accurate were the predictions
##make a model that reads 2023 data ,if properly avaliable, and makes prediction for a country
##make study of Na's and OLS, and explain them

#filter massive world bank data
def data_of_2023():
   world_data_path=os.path.join("2023 data","WDICSV.csv")
   world_bank_mega_data=read_csv(world_data_path)
   selected_cols=["Country Name","Country Code","Indicator Name","2021","2022","2023"]
   original_data=world_bank_mega_data[selected_cols]
   filtered_data=original_data[original_data["Indicator Name"].isin(included_vars)].reset_index(drop=True).copy()
   filtered_data.to_csv(os.path.join("2023 data","23 filtered.csv"),index=False)

#data_of_2023()

#data_of_2023
def many_2023_datas():
   data=read_csv(os.path.join("2023 data","23 filtered.csv"))
   countries=data["Country Name"]
   for country in countries:
       country_2023=data[data["Country Name"]==country].reset_index(drop=True).copy()
       country_2023=country_2023[["Indicator Name","2021","2022","2023"]] #we need 2021 and 2023 to fill missing na with interpolate and ffill
       country_2023.columns = ['Years'] + list(country_2023.columns[1:]) #replace indicator name with columns
       country_2023=country_2023.set_index("Years").T
       country_2023=country_2023.interpolate()
       country_2023=country_2023.fillna(method="ffill")
       country_2023=country_2023.drop([country_2023.index[0],country_2023.index[1]])  #remove 2021 and 2023
       country_2023.to_csv(os.path.join("2023 data",f"{country}.csv"),index=False)
   print("all done!")   

#many_2023_datas()

#def War_Predictor_X_Year(country1,country2,find_folder):
 
#War_Predictor_X_Year("United States","China","2023 data")






                         ##Building GUI, and making predictor for many years##
        ############################################################################


#let us make a data frames just like 2023 data , so that we can see how accurate
#our predictor is with regards to the past


os.makedirs("data for predictions",exist_ok=True)

def data_for_prediction(save_folder):
   world_data_path=os.path.join("2023 data","WDICSV.csv")
   big_data_frame=filter_country_data("world",world_data_path,all_years=True,skiprows=False,country_name=True)
   big_data_frame.to_csv(os.path.join("data for predictions","Big_data_for_prediction.csv"),index=False)
   data=big_data_frame
   years=big_data_frame.columns[4:]
   countries=big_data_frame["Country Name"]
   for year in years:
       os_path=os.path.join(save_folder,f"{year}")
       os.makedirs(os_path,exist_ok=True)
       years_valid=[str(year_) for year_ in range(1960,2024)]
       indx=int(year)
       for country in countries:
           country_=data[data["Country Name"]==country].reset_index(drop=True).copy()
           country_=country_[["Indicator Name"]+years_valid] #we need older years
           country_.columns = ['Years'] + list(country_.columns[1:]) #replace indicator name with columns
           country_=country_.set_index("Years").T
           country_=country_.drop(columns=["Literacy rate, adult total (% of people ages 15 and above)","Energy imports, net (% of energy use)","CPIA gender equality rating (1=low to 6=high)","Central government debt, total (% of GDP)","Unemployment, male (% of male labor force) (national estimate)"])
           country_=country_.interpolate()
           country_=country_.fillna(method="ffill")
           country_=country_[country_.index==year]
           country_.to_csv(os.path.join(os_path,f"{country}.csv"),index=False)

##data_for_prediction("data for predictions") WARNING This function takes more than 30 minute to complete 
##please do not run it unless you have to, evidence of it's effectivness is that it created 63  files with 200+ values each
##which it would have taken me very very very long to do manually

def all_country_names_list_world_bank():
    path=os.path.join("2023 data","23 filtered.csv")
    data_2023=read_csv(path)
    country_list=set(data_2023['Country Name'])
    all_world_countries=open("All_Countries_OF_The_world.txt","w")
    for country in country_list:
        all_world_countries.write(f"{country}\n")
    
##LIST OF COUNTRIES, Will be used to automate mass Predictions
#all_country_names_list_world_bank()
all_world_country=open("All_Countries_OF_The_world.txt","r")
country_list=[i.strip() for i in all_world_country]


        
#I tested model using test_the_model(conflicts) (FUNCTION BELOW)
#I used older version of function below to test the conflict predictor innacuracy
#using excell I calculated that average innacuracy of the war was 3.7 years too late!
#thus I will add -3.7 to the prediction by default in the War_Predictor function so it is more accurate in calculating wars
#I did not write code twice to avoid duplication and ugly code




###################FINALLY THE MODEL ITSELF!!#############################################################################################
############################################################################################################################################

def War_Predictor_X_Year_CORRECTED(country1,country2,find_folder):
   country1_path=os.path.join(find_folder,f"{country1}.csv")
   country2_path=os.path.join(find_folder,f"{country2}.csv")
   cntry1=read_csv(country1_path)
   cntry2=read_csv(country2_path)
   cntry1_dict={}
   cntry2_dict={}
   for var in included_vars:
       cntry1_dict[var]=cntry1[var]
       cntry2_dict[var]=cntry2[var]
   try:
       prediction1=int(prediction_model_maker(cntry1_dict))
       prediction2=int(prediction_model_maker(cntry2_dict))
       the_Prediction=(prediction1+prediction2)/2-3.7
       print(f"years before the war for {country1}: {prediction1},\nyears before the war for {country2}:{prediction2}")
       print(f"years before the war between {country1} and {country2}: {the_Prediction}")
       return the_Prediction
   except:
       print(f"not enough data avaliable for prediction of interstate war between {country1} and {country2}") 
       return None

def War_Predictor_2(year,country1,country2):
   os_path=os.path.join("data for predictions",year)
   return War_Predictor_X_Year_CORRECTED(country1,country2,os_path)


 #WE HAD TO CHANGE SOME NAMES IN THE WARS CSV!
#TO FIT THE OFFICIAL WORLD BANK NAMES SO FOR EXAMPLE: Vietnam---> Viet Nam
#Soma names have commas in their name so we have to change them manually


#This creates df that show model accuracy , closer to 0 the accuracy the beter
def test_the_model(conflicts_csv):
   conflicts_new=conflicts_csv.copy()
   prediction_accuracy=[]
   for row in conflicts_new.itertuples():
       
       year=str(row.year_of_start)
       if int(year)<1962:  #for some reason when I created data frames for prediction, due to my mistake 1960,1961 folders were missed 
           #since it takes excedeingly long time to rerun that function I will skip America-Cuba conflict for time's sake
           prediction_accuracy.append("Na")  
           continue      
       combatant1=row.combatant1
       if row.war=="Iran-Iraq_War":
           combatant1="Iran, Islamic Rep."
       combatant2=row.combatant2
       if row.war=="Six_Day_War" or row.war=="Yom-Kippur_War":
           combatant2="Egypt, Arab Rep."
       year=str(row.year_of_start)
       prediction=War_Predictor_2(year,combatant1,combatant2)
       if prediction==None:
           prediction_accuracy.append("Na")
       else:
           prediction_accuracy.append(0-prediction)
   conflicts_new["War Predictor Prediction Accuracy"]=prediction_accuracy
   conflicts_new.to_csv("Prediction_accuracy_of_War_Predictor.csv",index=False)


##WAR PREDICTION MODEL HAS BEEN MODIFIED AND REMADE!!
##
test_the_model(conflicts)

