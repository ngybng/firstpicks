#Import libraries.
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

#Scrape all recorded college champions with corresponding years from NCAA website.
url = 'https://www.ncaa.com/history/basketball-men/d1'
html_content = requests.get(url).text
soup = BeautifulSoup(html_content, "lxml")
article = soup.find("article", attrs={"class": "node-history overflowable-table-region layout--content-left"})
article_data = article.tbody.find_all('tr')

champions = []
years = []
for data in article_data:
    x = data.find_all('td')[1]
    y = data.find_all('td')[0]
    champions.append(x.text)
    years.append(y.text)
                     
champions = pd.Series(champions)
years = pd.Series(years)
champions = champions.str.extract(r'([^(\d]+)')
champions['years'] = years
champions.rename({0: 'champions'}, axis = 1, inplace = True)
champions.champions = champions.champions.str.strip()


#Scrape name of first picks in NBA draft.
url = 'https://en.wikipedia.org/wiki/List_of_first_overall_NBA_draft_picks'
html_content = requests.get(url).text
soup = BeautifulSoup(html_content, 'lxml')
article = soup.find('table', attrs = {'class': 'wikitable plainrowheaders sortable', 'summary': 'Draft (sortable), Selected by (sortable), Player (sortable), Nationality (sortable), College/high school/former club (sortable), PPG (sortable), RPG (sortable), APG (sortable) and References'})
article_data = article.tbody.find_all('tr')

first_picks = []
for data in article_data[2:]:
   x = data.find('th').find('span')
   first_picks.append(x.text)
   
first_picks.reverse() #Reverse to match order in champions dataframe
first_picks = pd.Series(first_picks, name = 'first_pick')
first_picks = first_picks.str.strip()

champions['first_picks'] = first_picks
champions['first_picks'] = champions['first_picks'].str.replace(' ', '_') #Replace space with underscore for extracting from url purposes later on.
champions.dropna(inplace = True)

#Scrape schools first picks went to from their wikipedia page.            

def extract_sch(article):
    article_data = article.tbody.find_all('tr')
        
    for data in article_data:              
                
        if data.find('td') == None:
            pass
        elif data.find('td') != None:
            td = data.find('td', attrs = {'class': 'plainlist'})
            if td == None:
                pass
            elif td != None:
                school = td.find('a')
                    
                if school == None:
                    schools.append('None')
                else:
                    schools.append(school.text)

s = []
for element in champions['first_picks']:
    schools = []
    s.append(schools)
     

    url_format = 'https://en.wikipedia.org/wiki/{}'.format(element)
    #Account for exceptions that don't fit element format above.
    if element == 'Larry_Johnson':
        url_format = 'https://en.wikipedia.org/wiki/Larry_Johnson_(basketball,_born_1969)'
    elif element == 'Jimmy_Walker':
        url_format = 'https://en.wikipedia.org/wiki/Jimmy_Walker_(basketball,_born_1944)'
    elif element == 'Jim_Barnes':
        url_format = 'https://en.wikipedia.org/wiki/Jim_%22Bad_News%22_Barnes'
    html_soup = requests.get(url_format).text
    soup = BeautifulSoup(html_soup, 'html.parser')
    article = soup.find('table', attrs = {'class': r'infobox vcard'})
    
    if element == "Shaquille_O'Neal":
        article = soup.find('table', attrs = {'class': 'infobox biography vcard'})
        
    if article == None:
        url_format = 'https://en.wikipedia.org/wiki/{}'.format(element + '_(basketball)')
        html_soup = requests.get(url_format).text
        soup = BeautifulSoup(html_soup, 'html.parser')
        article = soup.find('table', attrs = {'class': 'infobox vcard'})
        extract_sch(article)
        
    
    else:
        extract_sch(article)

            

#Extract school first picks drafted out of from list 's'
college = []
for row in s:
    if len(row) >=1:
         college.append(row[-1])
    else: 
        college.append('')
college = pd.Series(college, name = 'drafted_out_of')
champions['drafted_out_of'] = college

#Create new column to compare if champions and school of first pick matches.
champions['match'] = np.where(champions['champions'] == champions['drafted_out_of'], 'Yes', "No")

#Replace underscore in first pick names with space for aesthetics.
champions['first_picks'] = champions['first_picks'].str.replace('_', ' ')  

#Export dataframe to csv.
champions.to_csv('champions.csv', index = False)

#Filter to answer question statement.
champions[champions.match == 'Yes']

