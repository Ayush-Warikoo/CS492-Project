from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tabulate import tabulate
import sys
import urllib
import urllib.request
from bs4 import BeautifulSoup
import os


# test comment

# pip install urllib
# url = "https://twitter.com/home"
# page = urllib.request.urlopen(url)

# get all the files in the directory ./News and store them in a list

def getTopicSentimentAnalysisTable(profile):
  profile_folder = "./" + profile
  trending_topic_files = []
  for file in os.listdir(profile_folder):
      if file.endswith(".html"):
          trending_topic_files.append(os.path.join(profile_folder, file))
  table = []
  for file in trending_topic_files:
    positive, negative, neutral, sentiment_sum = 0, 0, 0, 0
    with open(file) as fp:
      soup = BeautifulSoup(fp, 'html.parser')
      tweets = soup.findAll(attrs={'data-testid': 'tweetText'})
      for index, tweet in enumerate(tweets):
          if tweet.text:
              # print(tweet.text)
              vs = analyzer.polarity_scores(tweet.text)
              if vs['compound'] >= 0.05:
                positive += 1
              elif vs['compound'] <= -0.05:
                negative += 1
              else:
                neutral += 1
              sentiment_sum += vs['compound']
    # parse file name
    file_name = os.path.splitext(os.path.basename(file))[0].replace("-", " ")
    table.append([file_name, positive, negative, neutral, sentiment_sum/len(tweets)])
  print(tabulate(table, headers=[profile + ' - Topic', 'Pos', 'Neg', 'Neu', 'Ave'], tablefmt='orgtbl'))
  return table
        
# Looks at integrating web history
# Certain tweets being emailed out

if __name__ == '__main__':
  analyzer = SentimentIntensityAnalyzer()
  getTopicSentimentAnalysisTable("News")
  getTopicSentimentAnalysisTable("Tech")
  getTopicSentimentAnalysisTable("Celebs")

