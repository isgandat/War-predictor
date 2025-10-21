import numpy as np
import pandas as pn
from pandas import read_csv,DataFrame,isna,concat
from statsmodels.api import OLS,add_constant
import tkinter as tk
import os 
####### BUIDLING COMPLETE COUNTRIES  DATASET ###########################################################################################
######Step 5-9 from the plan##########################################################################################

#1.1) Build a shopping list of data, dictionary of countries and years we are interested in>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#which countries are we interested in? Make set of countries from the 29 conflicts you wrote dow
conflicts=read_csv("csv_of_wars.txt")
def shopping_list():
  #dictionary that will help me utilize for which country which year I need to search and filter
  years_countries={}
  for row in conflicts.itertuples(): #.itertuples() method allows df rows to be itirated
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
  #print(years_countries)
  return years_countries

years_countries=shopping_list()
#with open("what_data_to_look_for.txt","w") as f:  
#    for key,val in years_countries.items():
#        f.write(f"{key}: {val}\n")
#This writes down in what_data_to_look_for.txt what I have to look for to download ,
#countries,and years that we are interested in 
#step 5 complete let's move to step 6: search and download data




#1.2)Download,filter and format data to fit my purposes>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#step6: complete, on World Bank data website I found and donwloaded bulk data for 30 of 32 countries
#problem is , 2 countries I did not find data for were Soviet Union and Yugoslavia 
#these two countries do not exist anymore

#FOrmat of World bank data I downloaded: Data is per country
# Rows are variables (and there are over thousand different variables) 
#columns are years starting from 1960 finishing with 2023

##see step 7 from steps to building project.txt, it explains how I am going to filter data  now 

def study_Data_for_variables():
 economic_keyword={"GDP","capita","poverty","inflation","unemployment","exchange","interest","gas","oil","energy","urban","rural","military","trade"}
 demographic_keyword={"population","age","gender","religious","religion","male","female","fertility","population density","ethnic"}
 political_keyword={"regime","war","majority","ideology","territory","area"}  
 keywords=economic_keyword.union(demographic_keyword).union(political_keyword) #total keywords that will help me find desirable variables in csvs
 all_matching_variables=set() 
 unfiltered_variables=open("unfiltered_matching_variables.txt","w")
 usa_data_path=os.path.join("big data","US.csv")
 usa_study_case=read_csv(usa_data_path)
 #print(usa_study_case)
 total_variables=usa_study_case["Indicator Name"] #this is where all the 1400+ variables are stored
 for variable in total_variables:
    if any(keyword in variable for keyword in keywords):
       all_matching_variables.add(variable)
       unfiltered_variables.write(f"{variable}\n")
 return all_matching_variables

#Study_Data_for_variables()

#unfiltered_matching_variables=study_Data_for_variables()           This code is run just once, to write on unfiltered matching_variables.txt
#                                                                   however if someone wishes, they can have unfiltered variables as python set too


#Analysis From the Study_Data_For_Variables()
#the csv really starts from 5th row, so all the first 4 rows must be skipped for all csv's, in case of US i just deleted it manually
#                for others I will use skiprow arguement in the read_csv function
#the filtering cut the varaibles in half (747) which is still a huge number, 
#theese variables are saved on unfiltered_matching_variables.txt , i will manually copy it 
# and paste it on the new txt file called handy_picked_variables.txt, where I will handy pick varaibles by hand
#since this picking is based on taste, there is not a very good way to filter everything automatically
#and handipicking will probably not take very long since some variables are easily visible to be not useful to us
#After some time I finished hand picking variables, there are 15 of them 
selected_variables=set()
for i in open("handy_picked_variables.txt","r"):
   selected_variables.add(i.strip())
#NOW selected_variables set and countries_years dict will help us filter datasets 
def filter_country_data(country,the_path,all_years=False):
   if all_years:
      years_of_interest=[str(i) for i in range(1960,2024)] #2023 is max year usually
   else:
    years_of_interest=years_countries.get(country)
    years_of_interest=[str(year) for year in years_of_interest]
   columns_of_interest=["Indicator Name"]+years_of_interest 
   #columns_of_interest is columns we will extract from big dataframe to create data frame that we care about
   original_data=read_csv(the_path,skiprows=4)
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


#Problem detected!! For some conflicts 10 years countdown starts from before 1960, thus we need to  change year_countries to remove such years
for key,value in years_countries.items():
   years_countries[key]=[k for k in value if int(k)>=1960]
   
#big_data_filtrer() #finished! The filtered data downloaded in filtered data file





#1.3) dealing with Na's >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#I will use transplant method: replace Na's by World bank regional or world data
regions={}
def region_filterer():
   for file in os.listdir("regions"):
      region_name=file[:-4]
      regions[region_name]=list()
      the_path=os.path.join("regions",file)
      the_storage_path=os.path.join("regions_filter",file)
      filtered_data=filter_country_data(region_name,the_path,all_years=True)
      filtered_data.to_csv(the_storage_path,index=False)

#region_filterer()  #this code should be run just once, so the files are filtered out once


#START OF CHATGPT API BLOCK##
#regional data is full and has potential for filling country Na's too, I will utilize Ai to map countries to regions, and then use that
#mapping to use regional data cells as transplant for country data sets
import json
from openai import OpenAI
import difflib  #to find closes match to my regions from AI response
#client = OpenAI(api_key="SECRET")

#def askai(prompt, tokenlimit):
  #  answer = client.chat.completions.create(
  #      model="gpt-3.5-turbo",
  #      messages=[{"role": "user", "content": prompt}],
  #      max_tokens=tokenlimit
  #  )
  #  return answer.choices[0].message.content.strip()

def map_countries_to_regions():
   jsonstorage="Country_Region_Dict.txt"
   country_list=years_countries.keys()
   region_list=regions.keys()
   for country in country_list:
      if country=="UK":
         regions["eu"].append("UK")
      else:
       prompt=f"out of regions list: {region_list} which one does {country} belong to? Your response should be single element just EXACT copy from the regions list, if you want to say something else just find best match in list. Don't write aything of your own"
       ai_answer=askai(prompt,10)
       ai_answer= difflib.get_close_matches(ai_answer, region_list, n=1)
       ai_answer=ai_answer[0]
       print(ai_answer)
       regions[ai_answer].append(country)
   print(regions)
   with open(jsonstorage,"w") as file:
            json.dump(regions,file)

#map_countries_to_regions()   code as I said should run only once to write to Json, because it uses api tokens which cost money
#the Ai sorted mostly well, there are some misorting here ,and there but nothing I can't fix manually (Cyprus should have been in EU instead of
#eastern Europe) (and Cambodia belongs to East Asia rather than Southern Asia)
#Even though Cyprus is geographically Middle East, for most of its history it enjoyed relatively good economic condintions, and is now part of Eu
regions=json.load(open("Country_Region_Dict.txt","r"))
#amazing! Now we have regions and countries dictionary, but we need to switch country and key,  and rather to change Ai communicaton code
#which will cost me extra effort and money, i  will just run this short code
regions2=dict()
for key,val in regions.items():
   for country in val:
      regions2[country]=key

#END OF CHATGPT API BLOCK##


def Na_filler(country_file,country_folder,region_folder,store_folder): #NOTe! when you open a filtered data do not do skiprows, since data is already stripped of extra cols
   country=country_file[:-4]
   corresponding_region=f"{regions2[country]}.csv"
   country_path=os.path.join(country_folder,country_file)
   region_path=os.path.join(region_folder,corresponding_region)
   country_csv=read_csv(country_path)
   region_csv=read_csv(region_path)
   tot_cls=0
   Na_s=0
   Na_replacement=0
   for index,row in country_csv.iterrows():
      for col in country_csv.columns:
         tot_cls+=1
         if isna(row[col]):
            Na_s+=1
            if not isna(region_csv.at[index,col]):
             Na_replacement+=1
             country_csv.at[index,col]=region_csv.at[index,col]
            else:
               continue
   store_path=os.path.join(store_folder,country_file)
   country_csv.to_csv(store_path,index=False)
   return tot_cls,Na_s,Na_replacement  #this will help us find out the Na coverage and effectivness of this method


def Na_executioner():
   country_folder="filtered data"
   cls=0
   Nas=0
   replacedNas=0
   for country_file in os.listdir(country_folder):
      cl,n,rep=Na_filler(country_file,country_folder,"regions_filter","Na_filter_1")
      cls+=cl
      Nas+=n
      replacedNas+=rep
   print(f"total cells: {cls} total Nas: {Nas} percentage of cell Na's : {Nas/cls*100} Na replacement rate: {replacedNas/Nas*100}")
#Na_executioner()
#total cells: 7785 total Nas: 2952 percentage of cell Na's : 37.91907514450867 Na replacement rate: 28.184281842818425

#Round 2 of Na filtering:
os.makedirs("Na_filter_2",exist_ok=True)
#we used regions to fill in Na data, now let us use the world data! World data will fill in some gaps

def World_NaN_Terminator(country_folder,store_folder):
      #after world csv is shaved off
      world_csv=filter_country_data("world","world__.csv",all_years=True)
      world_csv.to_csv("world.csv",index=False)
      cls=0
      Nas=0
      replacedNas=0
      
      for filename in os.listdir(country_folder):
       country_path=os.path.join(country_folder,filename)
       country_csv=read_csv(country_path)
       print(world_csv["Indicator Name"].equals(country_csv["Indicator Name"]))
       tot_cls=0
       Na_s=0
       Na_replacement=0
       for index,row in country_csv.iterrows():
          for col in country_csv.columns:
            tot_cls+=1
            if isna(row[col]):
              Na_s+=1
              if not isna(world_csv.at[index,col]):
               Na_replacement+=1
               country_csv.at[index,col]=world_csv.at[index,col]
              else:
                 continue
       store_path=os.path.join(store_folder,filename)
       country_csv.to_csv(store_path,index=False)
       cls+=tot_cls
       Nas+=Na_s
       replacedNas+=Na_replacement
      print(f"total cells: {cls} total Nas: {Nas} percentage of cell Na's : {Nas/cls*100} Na replacement rate: {replacedNas/Nas*100} Na's left: {Nas-replacedNas}")

#World_NaN_Terminator("Na_filter_1","Na_filter_2")
#total cells: 7785 total Nas: 2120 percentage of cell Na's : 27.231856133590238 Na replacement rate: 17.830188679245282 Na's left: 1742

#Round 3 of Na filtering and formating of data
os.makedirs("Na_filter_3",exist_ok=True)
#I will finish the filtering by transposing matrix and filtering by interpolate, then by bfill and ffill and finally by filling completely
#empty cols by 0

def final_formater_country(file_country,store_folder,folder_country):
 open_path=os.path.join(folder_country,file_country)
 country=read_csv(open_path)
 country.columns = ['Years'] + list(country.columns[1:]) #remove Indicator Name and replace it with years since we are transposing matrix

 country=country.set_index("Years").T
 country=country.interpolate()
 country=country.fillna(method="bfill")
 country=country.fillna(method="ffill") 
 country=country.fillna(0) #this finally converts all the values of completely empty columns into 0's
 
 store_path=os.path.join(store_folder,file_country)
 country.to_csv(store_path,index=True) ##index must be true for transpose matrix when saving it as csv 

def Countries_final_data_form():
   folder="Na_filter_2"
   store="Na_filter_3"
   for file in os.listdir(folder):
      final_formater_country(file,store,folder)
   print("all done!")

#Countries_final_data_form()
#steps 1-9 complete!


   





####### BUIDLING  COMBIEND DATA FOR ECONOMETRICS MODEL##############################################################
##################STEPS 10-12 FROM##############################################################

#we already have a nicely formatted Na filled dataframes for all necessary countries
#now let us create a function that  will take as arguements year of start for war, two countries
#and based on that create a dataset which includes statistics of both countries , and is joined by year
#name of such data set will be the name of war from conflicts csv that I read in beginning
#add two columns, a war index that will keep track of which war this is in large dataframe, (and this will make merging easier)
#and years_before_the_war variable which will be dependent variable in the ols regression

def create_war_data_frame(country1_file,country2_file,year_of_start,country_folder):
   year_of_start=int(year_of_start)
   valid_years=[int(i) for i in range(year_of_start-10,year_of_start+1) if i>=1960]
   country1_path=os.path.join(country_folder,country1_file)
   country2_path=os.path.join(country_folder,country2_file)
   country1_csv=read_csv(country1_path)
   country2_csv=read_csv(country2_path)
   country2_col_names=["Years"]+[(i+" 2") for i in list(country2_csv.columns[1:])] #add 2 to differentiate between countries
   country2_csv.columns=country2_col_names
   country1_col_names=["Years"]+list(country1_csv.columns[1:]) #add 2 to differentiate between countries
   country1_csv.columns=country1_col_names
   country1_csv=country1_csv[country1_csv["Years"].isin(valid_years)].copy()
   country2_csv=country2_csv[country2_csv["Years"].isin(valid_years)].copy()
   joined_data_frame=country1_csv.merge(country2_csv,on="Years")
   return joined_data_frame
   
os.makedirs("war_dfs",exist_ok=True)

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
       x=create_war_data_frame(country1,country2,year_of_start_,openfolder)
       x2=create_war_data_frame(country2,country1,year_of_start_,openfolder)
       years_before_the_war=[(year_of_start_-i) for i in list(x["Years"])]
       x["years before the war"]=years_before_the_war
       x2["years before the war"]=years_before_the_war
       x["War tracker"]=thewar  
       x2["War tracker"]=f"{thewar} v2"
       store_path=os.path.join(storagefolder,f"{thewar}.csv")
       x.to_csv(store_path,index=False)
       store_path2=os.path.join(storagefolder,f"{thewar} v2.csv")
       x2.to_csv(store_path2,index=False)
    print("all done!")

#create_all_war_dfs("war_dfs","Na_filter_3",conflicts)
      
      
#now let us unify this into single data set!
os.makedirs("unified dataframe for ols",exist_ok=True)

def unify_data_frames(open_folder,store_folder):
   concat_list=[]
   for war_df in os.listdir(open_folder):
      file_path=os.path.join(open_folder,war_df)
      concat_list.append(read_csv(file_path))
   big_df=concat(concat_list,axis=0)
   save_path=os.path.join(store_folder,"Final_unified_data.csv")
   big_df.to_csv(save_path,index=False)
   print("all done")

#unify_data_frames("war_dfs","unified dataframe for ols")




####### BUIDLING  ECONOMETRIC PREDICTION MODEL##############################################################
##################STEPS 13-16 FROM THE PLAN##############################################################
final_data_path=os.path.join("unified dataframe for ols","Final_unified_data.csv")
final_data=read_csv(final_data_path)
excluded_vars=['War tracker',"Years",'years before the war'] #exclude dependent variable , and non-numerical variables
included_vars=final_data.columns.difference(excluded_vars)
y=final_data['years before the war']
x=final_data[included_vars]
x=add_constant(x)
model=OLS(y,x)
results=model.fit()
#OLS_results=open("OLS_results.txt","w")
#OLS_results.write(str(results.summary()))
#OLS_results.close()

#let's create a coefficients dictionary from OLS results that will be used for prediction model
#extract the coefficients 
coefficents_from_ols=results.params #this df kind of structure
prediction_dict={}


def prediction_model_maker(input_dict):
   for i in included_vars:
      coef=coefficents_from_ols[i]
      prediction_dict[i]=coef
   prediction_dict["constant"]=coefficents_from_ols[0]
   prediction=sum(coefficents_from_ols["constant"]+coefficents_from_ols[var]*input_dict[var] for var in input_dict)
   return prediction

#downloaded massive world bank data and only saved data for 2023
os.makedirs("2023 data",exist_ok=True)
def data_of_2023():
 world_data_path=os.path.join("2023 data","WDICSV.csv")
 world_bank_mega_data=read_csv(world_data_path)
 selected_cols=["Country Name","Country Code","Indicator Name","2023"]
 original_data=world_bank_mega_data[selected_cols]
 filtered_data=original_data[original_data["Indicator Name"].isin(selected_variables)].reset_index(drop=True).copy()
 filtered_data.to_csv(os.path.join("2023 data","23 filtered.csv"),index=False)
 #also make a world csv  for 2023 that will be a Na filler 
 world=read_csv("world.csv")
 world_inds=["Indicator Name","2023"]
 world=world[world_inds]
 world.to_csv(os.path.join("2023 data","world_in23.csv"),index=False)

#data_of_2023()


def many_2023_datas():
   data=read_csv(os.path.join("2023 data","na_filtered.csv"))
   countries=data["Country Name"]
   for country in countries:
       country_2023=data[data["Indicator Name"]==country].reset_index(drop=True).copy()
       country_2023.to_csv(f"{country}".csv)
   print("all done!")   

many_2023_datas()
#fill_na_2023() it is finally ready 