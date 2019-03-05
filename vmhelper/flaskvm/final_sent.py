# -*- coding: utf-8 -*-
import json
from textblob import TextBlob
import re
import pandas as pd
class sentimental_analysis():
    Brand=''
    Location=''
    def __init__(self, brand,location):
        self.Brand = brand
        self.Location=location
    def strip_non_ascii(self,string):
        ''' Returns the string without non ASCII characters'''
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)
    def analyse(self):
        data = []
        with open('flaskvm/'+self.Brand+'.json') as f:
            for line in f:
                if line=='\n':
                    continue
                data.append(json.loads(line))
        
        
        eng_data = []
        if self.Location=='all' or self.Location=='All' or self.Location=='ALL':
            for i in range(0,len(data)):
                if data[i]['lang']=='en' :
                    eng_data.append(data[i])
        else :
            for i in range(0,len(data)):
                loc= data[i]['user']['location']
                loc=str(loc).lower()
                if data[i]['lang']=='en' and loc== self.Location.lower():
                    eng_data.append(data[i])
        del data[:]
        tweets = []
        tweets_inf = []
        tweets_n = []
        tweets_p = []
        self.positivec=0
        self.negativec=0
        self.neutralc=0
        
        
        
        for i in range(len(eng_data)):
            tweet= dict()
            tweet['orig'] = eng_data[i]['text']
            tweet['id'] = eng_data[i]['id']
            tweet['pubdate'] = eng_data[i]['created_at']
            tweet['user_id'] = eng_data[i]['user']['id']
            tweet['favourites_count'] = eng_data[i]['user']['favourites_count']
            tweet['followers_count'] = eng_data[i]['user']['followers_count']
            tweet['friends_count'] = eng_data[i]['user']['friends_count']
            tweet['location'] = eng_data[i]['user']['location']
            tweet['name'] = eng_data[i]['user']['name']
            tweet['screen_name'] = eng_data[i]['user']['screen_name']
            tweet['statuses_count'] = eng_data[i]['user']['statuses_count']
            tweet['verified'] = eng_data[i]['user']['verified']
            tweet['brand']=self.Brand
        
            if re.match(r'^RT.*', tweet['orig']):
                        continue
            
            tweet['clean'] = tweet['orig']
            
            # Remove all non-ascii characters
            tweet['clean'] = self.strip_non_ascii(tweet['clean'])
            
            # Normalize case
            tweet['clean'] = tweet['clean'].lower()
            
            # Remove URLS. (I stole this regex from the internet.)
            tweet['clean'] = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', tweet['clean'])
            
            # Fix classic tweet lingo
            tweet['clean'] = re.sub(r'\bthats\b', 'that is', tweet['clean'])
            tweet['clean'] = re.sub(r'\bive\b', 'i have', tweet['clean'])
            tweet['clean'] = re.sub(r'\bim\b', 'i am', tweet['clean'])
            tweet['clean'] = re.sub(r'\bya\b', 'yeah', tweet['clean'])
            tweet['clean'] = re.sub(r'\bcant\b', 'can not', tweet['clean'])
            tweet['clean'] = re.sub(r'\bwont\b', 'will not', tweet['clean'])
            tweet['clean'] = re.sub(r'\bid\b', 'i would', tweet['clean'])
            tweet['clean'] = re.sub(r'wtf', 'what the fuck', tweet['clean'])
            tweet['clean'] = re.sub(r'\bwth\b', 'what the hell', tweet['clean'])
            tweet['clean'] = re.sub(r'\br\b', 'are', tweet['clean'])
            tweet['clean'] = re.sub(r'\bu\b', 'you', tweet['clean'])
            tweet['clean'] = re.sub(r'\bk\b', 'OK', tweet['clean'])
            tweet['clean'] = re.sub(r'\bsux\b', 'sucks', tweet['clean'])
            tweet['clean'] = re.sub(r'\bno+\b', 'no', tweet['clean'])
            tweet['clean'] = re.sub(r'\bcoo+\b', 'cool', tweet['clean'])
            
            # Emoticons?
            # NOTE: Turns out that TextBlob already handles emoticons well, so the
            # following is not actually needed.
            # See http://www.datagenetics.com/blog/october52012/index.html
            # tweet['clean'] = re.sub(r'\b:\)\b', 'good', tweet['clean'])
            # tweet['clean'] = re.sub(r'\b:D\b', 'good', tweet['clean'])
            # tweet['clean'] = re.sub(r'\b:\(\b', 'sad', tweet['clean'])
            # tweet['clean'] = re.sub(r'\b:-\)\b', 'good', tweet['clean'])
            # tweet['clean'] = re.sub(r'\b=\)\b', 'good', tweet['clean'])
            # tweet['clean'] = re.sub(r'\b\(:\b', 'good', tweet['clean'])
            # tweet['clean'] = re.sub(r'\b:\\\b', 'annoyed', tweet['clean'])
            
            # Create textblob object
            tweet['TextBlob'] = TextBlob(tweet['clean'])
            
            # Correct spelling (WARNING: SLOW)
            #tweet['TextBlob'] = tweet['TextBlob'].correct()
            
            tweets.append(tweet)

        
        del eng_data[:]
        for tweet in tweets:
            tweet['polarity'] = float(tweet['TextBlob'].sentiment.polarity)
            tweet['subjectivity'] = float(tweet['TextBlob'].sentiment.subjectivity)
        
            if tweet['polarity'] >= 0.1:
                tweet['sentiment'] = 'positive'
                self.positivec+=1
                tweets_p.append(tweet)
            elif tweet['polarity'] <= -0.1:
                tweet['sentiment'] = 'negative'
                self.negativec+=1
            else:
                tweet['sentiment'] = 'neutral'
                tweets_n.append(tweet)
                self.neutralc+=1
            if tweet['followers_count']>=1000 and tweet['polarity']>=0:
                tweets_inf.append(tweet)
                

        self.tweets_sorted = sorted(tweets, key=lambda k: k['pubdate'])
        df=pd.DataFrame(self.tweets_sorted)
        df.to_csv('flaskvm/static/analysed_tweets.csv', encoding='utf-8', index=False)

        self.tweets_sorted_p = sorted(tweets_p, key=lambda k: k['polarity'])
        df=pd.DataFrame(self.tweets_sorted_p)
        df.to_csv('flaskvm/static/analysed_tweets_p.csv', encoding='utf-8', index=False)

        self.tweets_sorted_n = sorted(tweets_n, key=lambda k: k['polarity'])
        df=pd.DataFrame(self.tweets_sorted_n)
        df.to_csv('flaskvm/static/analysed_tweets_n.csv', encoding='utf-8', index=False)

        self.tweets_inf_sorted = sorted(tweets_inf, key=lambda k: k['followers_count'], reverse=True)
        df=pd.DataFrame(self.tweets_inf_sorted)
        df.to_csv('flaskvm/static/analysed_tweets_inf.csv', encoding='utf-8', index=False)
    def get_tweets(self):
        return self.tweets_sorted
    def get_tweets_inf(self):
        return self.tweets_inf_sorted
    def get_tweets_p(self):
        return self.tweets_sorted_p
    def get_tweets_n(self):
        return self.tweets_sorted_n
    def get_positive_tweets_count(self):
        return self.positivec
    def get_negative_tweets_count(self):
        return self.negativec
    def get_neutral_tweets_count(self):
        return self.neutralc