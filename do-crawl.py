from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import subprocess
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
        posts.loc[idx, 'Content'] = post_soup('div', 'content-body question-content')[0]
        posts.loc[idx, 'Link'] = post_url
    posts['Title'] = posts['Title'].map(str).str.replace('^\n\s{2,}', '\n<b>').str.replace('\n\s{2,}', '\n</b>')
    return posts
def filter_by_kw(posts, keywords = ['openlitespeed', '[^to]ols', 'cyberpanel', 'lsws', 'litespeed', \
               'lightspeed', 'open-lite-speed']):
    kw_str = '|'.join(keywords)
    return posts.loc[posts['Title'].str.contains(kw_str, regex=True, case=False) |\
                           posts['Content'].map(str).str.contains(kw_str, regex=True, case=False)]
def export2csv(filename='DO_forum.csv'):
    filtered_posts.to_csv(filename)

def export2txt(filename='DO_forum.txt'):
    filtered_posts.to_csv(filename, index=False, sep='\n', header=False)

def line_prepender(filename='DO_forum.txt', line="Subject: Check DigitalOcean Forum"):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

if __name__ == "__main__":
    URLs = sys.argv[1:]
    
    if URLs == []:
        URLs = ["https://www.digitalocean.com/community/questions"]
    
    print('URLs for scrapping:', URLs)

    t0 = time.time()
    filtered_posts = pd.DataFrame(columns = ['Title', 'Link', 'Content'])
    for URL in URLs:
        posts = webscraper(URL)
        filtered_posts = pd.concat([filtered_posts, filter_by_kw(posts=posts)])
        t = time.time()
        print(t - t0)
        t0 = t

    if len(filtered_posts) != 0:
        # only export to csv and overwrite if there is filtered post 
        export2txt()
        # insert subject line on top of text file
        line_prepender(line='Content-Type: text/html; charset=US-ASCII')
        line_prepender()
        # make bashcommand
        bashCommand = "sendmail xxxx@gmail.com < DO_forum.txt"
        output = subprocess.check_output(['bash','-c', bashCommand])
    else:
        print('0 question matchs keywords so do nothing')
