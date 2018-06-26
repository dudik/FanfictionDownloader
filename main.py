from bs4 import BeautifulSoup
from time import sleep
import requests, os

wait = 1

req = requests.Session()
retries = requests.packages.urllib3.Retry(total = 5, backoff_factor = 1, status_forcelist = [ 502, 503, 504 ])
req.mount('https://', requests.adapters.HTTPAdapter(max_retries = retries))

def validate(name):
    for char in '<>:"/\|?*':
        name = name.replace(char, '')
    return name

def getSoup(url):
    res = req.get(url)
    sleep(wait)
    return BeautifulSoup(res.content, 'html.parser')

def download(url):
    soup = getSoup(url)
    title = soup.select('#profile_top b.xcontrast_txt')[0].text
    author = soup.select('#profile_top a.xcontrast_txt')[0].text
    summary = soup.select('#profile_top div.xcontrast_txt')[0].text
    details = soup.select('#profile_top .xgray')[0].text
    
    print('Downloading ' + title + ' by ' + author)
    if soup.select('#chap_select'):
        chapter = soup.select('#chap_select')[0].find('option', selected = True).contents[0].replace('.', ' -', 1)
    else:
        chapter = '1'
    print('Downloading Chapter ' + chapter.split(' - ')[0])
    
    info = '%s\r\n\r\nAuthor:\r\n%s\r\n\r\nSummary:\r\n%s\r\n\r\nDetails:\r\n%s\r\n\r\n%s\r\n\r\n' % (title, author, summary, details, url)
    storyText = ''
    for p in soup.select('#storytext p'):
        storyText += p.text + '\r\n\r\n'
    if soup.select('#chap_select'):
        data = info + 'Chapter ' + chapter + '\r\n\r\n' + storyText
        nextBtn = soup.find('button', class_ = 'btn', text = 'Next >')
        while nextBtn:
            soup = getSoup(prefix + nextBtn.get('onclick').replace("self.location='", '').replace("'", ''))
            chapter = soup.select('#chap_select')[0].find('option', selected = True).contents[0].replace('.', ' -', 1)
            print('Downloading Chapter ' + chapter.split(' - ')[0])
            storyText = ''
            for p in soup.select('#storytext p'):
                storyText += p.text + '\r\n\r\n'
            data += 'Chapter ' + chapter + '\r\n\r\n' + storyText
            nextBtn = soup.find('button', class_ = 'btn', text = 'Next >')
    else:
        data = info + storyText
    with open(path + validate(title) + '.txt', 'w', encoding='utf-8') as f:
        f.write(data)

prefix = 'https://www.fanfiction.net'

print('Fanfiction Downloader 1.0 by github.com/woafu')
url = input('Enter URL: ')

if 'www.fanfiction.net' in url:
    if 'www.fanfiction.net/s/' in url:
        path = ''
        download(url)
    else:
        soup = getSoup(url)
        path = validate(soup.title.string.split(' |')[0]) + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        center = soup.find('center', style = 'margin-top:5px;margin-bottom:5px;')
        if 'www.fanfiction.net/u/' in url or center is None:
            for story in soup.select('.stitle'):
                if not os.path.isfile(path + '/' + validate(story.text) + '.txt'):
                    download(prefix + story.get('href'))
        else:
            firstPage = center.find('a', text = '1')
            if firstPage:
                soup = getSoup(prefix + firstPage.get('href'))
                center = soup.find('center', style = 'margin-top:5px;margin-bottom:5px;')
            nextLink = True
            while nextLink:
                for story in soup.select('.stitle'):
                    if not os.path.isfile(path + '/' + validate(story.text) + '.txt'):
                        download(prefix + story.get('href'))
                nextLink = center.find('a', text = 'Next »')
                if nextLink:
                    soup = getSoup(prefix + nextLink.get('href'))
                    center = soup.find('center', style = 'margin-top:5px;margin-bottom:5px;')
else:
    print('This URL is not supported')