# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 05:11:07 2018

@author: ARSY
"""

"""
LOADING DATA TWITTER

"""

from bs4 import BeautifulSoup as bs
import re,csv, os, pandas as pd,docx2txt
from tqdm import tqdm
from pattern.web import PDF
from bz2 import BZ2File as bz2

fData = '2019gantipresiden since 2018-11-01 until 2018-11-02 - Twitter Search.htm' #contoh nama file htm/htmlnya
fName = 'datapres.csv'#contoh nama csv yang diinginkan
bahasa = 'id' # atau 'en'
dataPath = 'D:/WinPython/notebooks/'#contoh letak data

# Loading Definisi-Definisi yang akan digunakan
def crawlFiles(dPath,types=None): # dPath ='C:/Temp/', types = 'pdf'
    if types:
        return [dPath+f for f in os.listdir(dPath) if f.endswith('.'+types)]
    else:
        return [dPath+f for f in os.listdir(dPath)]

def readBz2(file):
    with bz2(file, "r") as bzData:
        txt = []
        for line in bzData:
            try:
                txt.append(line.strip().decode('utf-8','replace'))
            except:
                pass
    return ' '.join(txt)

def LoadDocuments(dPath=None,types=None, file = None): # types = ['pdf','doc','docx','txt','bz2']
    Files, Docs = [], []
    if types:
        for tipe in types:
            Files += crawlFiles(dPath,tipe)
    if file:
        Files = [file]
    if not types and not file: # get all files regardless of their extensions
        Files += crawlFiles(dPath)
    for f in Files:
        if f[-3:].lower()=='pdf':
            try:
                Docs.append(PDF(f).string)
            except:
                print('error reading{0}'.format(f))
        elif f[-3:].lower()=='txt' or f[-3:].lower()=='dic':
            try:
                df=open(f,"r",encoding="utf-8", errors='replace')
                Docs.append(df.readlines());df.close()
            except:
                print('error reading{0}'.format(f))
        elif f[-3:].lower()=='bz2':
            try:
                Docs.append(readBz2(f))
            except:
                print('error reading{0}'.format(f))
        elif f[-4:].lower()=='docx':
            try:
                Docs.append(docx2txt.process(f))
            except:
                print('error reading{0}'.format(f))
        elif f[-3:].lower()=='csv':
            Docs.append(pd.read_csv(f))
        else:
            print('Unsupported format {0}'.format(f))
    if file:
        Docs = Docs[0]
    return Docs, Files

if __name__ == "__main__":
    urlPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    print('Loading Data: ', flush = True)
    allData = crawlFiles(dataPath, types='htm')
    Tweets, Username, waktu, replies, retweets, likes, Language =  [], [], [], [], [], [], []
    urlStatus, D = [], []
    # fData = allData[0]
    for fData in tqdm(allData):
        soup = bs(open(fData,encoding='utf-8', errors = 'ignore', mode='r'),'html.parser')
        data = soup.find_all('li', class_= 'stream-item')
        # t = data[0]
        for i,t in tqdm (enumerate(data)):
                # Loading tweet
                T = t.find_all('p',class_='TweetTextSize')[0]
                T = bs(str(T),'html.parser').text
                Tweets.append(T)
                # Loading UserName
                U = t.find_all('span',class_='username')
                U = bs(str(U[0]),'html.parser').text
                Username.append(U)
                # Loading Time
                T = t.find_all('a',class_='tweet-timestamp')[0]
                T = bs(str(T),'html.parser').text
                waktu.append(T)
                # Loading reply, retweet & Likes
                RP = t.find_all('span',class_='ProfileTweet-actionCountForAria')[0]
                RT = t.find_all('span',class_='ProfileTweet-actionCountForAria')[1]
                L  = t.find_all('span',class_='ProfileTweet-actionCountForAria')[2] 
                RP = int((bs(str(RP), "lxml").text.split()[0]).replace(',',''))
                RT = int((bs(str(RT), "lxml").text.split()[0]).replace(',',''))
                L = int((bs(str(L), "lxml").text.split()[0]).replace(',',''))
                replies.append(RP)
                retweets.append(RT)
                likes.append(L)
                # Loading Bahasa
                try:
                    L = t.find_all('span',class_='tweet-language')
                    L = bs(str(L[0]), "lxml").text
                except:
                    L =''
                Language.append(L)
                
                if RT>0:
                    urlS = str(t.find_all('small',class_='time')[0])
                    urlStatus.append(re.findall(urlPattern,urlS)[0])
                else:
                    urlStatus.append('')

    print('Saving Data to "%s" ' %fName, flush = True)
    N = len (Tweets)
    dfile = open(fName, 'w', encoding='utf-8', newline='')
    dfile.write('Time,Username,Replies, Retweets,Likes,Language,Tweet\n')
    with dfile :
        writer = csv.writer(dfile)
        for i in range(N):
            writer.writerow([waktu[i],Username[i],replies[i],retweets[i],likes[i],Language[i],Tweets[i]])
    dfile.close()
             
    print('All Finished', flush = True)
