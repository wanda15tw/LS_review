from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import sys
def webscraper(URL):
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'html5lib')
    questions = [(a.text, a['href']) for a in soup.find_all('a') if a.parent.name == 'h3']
    titles, links = list(zip(*questions))
    posts = pd.DataFrame({'Title':titles, 'Link':links, 'Content':''} )
    base_URL = 'https://www.digitalocean.com'
    for idx in range(len(links)):
        post_url = base_URL + links[idx]
        post_soup = BeautifulSoup(requests.get(post_url).text, 'html5lib')
        posts.loc[idx, 'Content'] = post_soup('div', 'content-body question-content')[0].text
    return posts
def filter_by_kw(posts, keywords = ['openlitespeed', 'ols', 'cyberpanel', 'lsws', 'litespeed', \
               'lightspeed', 'open-lite-speed']):
    kw_str = '|'.join(keywords)
    return posts.loc[posts['Title'].str.contains(kw_str, regex=True, case=False) |\
                           posts['Content'].str.contains(kw_str, regex=True, case=False)]
def export2csv(filename='DO_forum.csv'):
    filtered_posts.to_csv(filename)
if __name__ == "__main__":
    URLs = sys.argv[1:]
    
    if URLs == []:
        URLs = ["https://www.digitalocean.com/community/questions", \
                "https://www.digitalocean.com/community/questions?q=openlitespeed"]
    
    print('URLs for scrapping:', URLs)

    t0 = time.time()
    filtered_posts = pd.DataFrame(columns = ['Title', 'Link', 'Content'])
    for URL in URLs:
        posts = webscraper(URL)
        filtered_posts = pd.concat([filtered_posts, filter_by_kw(posts=posts)])
        t = time.time()
        print(t - t0)
        t0 = t
    export2csv()
