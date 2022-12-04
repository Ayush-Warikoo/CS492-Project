from selenium import webdriver
from selenium.webdriver.common.by import By
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import datetime
import csv

class TwitterScraper:
    def __init__(self, username, password, tag):
        self.analyzer = SentimentIntensityAnalyzer()
        self.driver = webdriver.Edge()
        self.visited_tweets = set()
        self.username = username
        self.password = password
        self.tag = tag

    def __exit__(self):
        # pass
        self.driver.close()

    def login_to_twitter(self, username, password):
        self.driver.get("https://twitter.com/i/flow/login")
        time.sleep(10)
        username_input = self.driver.find_elements(By.TAG_NAME, "input")[0];  
        username_input.send_keys(username)
        next_button = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")[2]
        next_button.click()
        time.sleep(2)
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input.send_keys(password)
        login_button = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")[2]
        login_button.click()
        time.sleep(10)

    # Noticed that on average each scroll uncovered 10 new tweets, increase num_scroll to get to desired number of tweets
    def extract_tweet_data(self, num_scroll=2, num_tweets=10):
        data = []
        # iterate num_scroll times
        for i in range(0, num_scroll):
            tweets = self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")
            trailing_tweets_num = min(num_tweets, len(tweets))
            for tweet in tweets[-1 * trailing_tweets_num:]:
                try:
                    # Check if unique tweet
                    if tweet in self.visited_tweets: continue
                    self.visited_tweets.add(tweet)
                    
                    # Extract tweet data
                    tweet_text = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='tweetText']").text.replace("\n", " ") or ""
                    tweet_reply = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='reply']").text or "0"
                    tweet_retweet = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='retweet']").text or "0"
                    tweet_like = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='like']").text or "0"
                    tweet_sentiment_score = self.analyzer.polarity_scores(tweet_text)["compound"]
                    tweet_sentiment = "pos" if tweet_sentiment_score > 0.05 else ("neg" if tweet_sentiment_score < -0.05 else "neu")
                    # tweet_url = tweet.find_elements(By.CSS_SELECTOR, "a[role='link']")[3].get_attribute("href")
                    # tweet_quote_retweet = self.extract_tweet_quote_retweets(tweet_url)
                    tweet_quote_retweet = "N/A"
                    data.append((tweet_text, tweet_reply, tweet_retweet, tweet_like, tweet_quote_retweet, tweet_sentiment_score, tweet_sentiment))
                    # print(tweet_text, tweet_reply, tweet_retweet, tweet_like, tweet_quote_retweet, tweet_sentiment_score, tweet_sentiment)
                except Exception as e:
                    continue
            if i < num_scroll - 1:
                self.scroll_down()
        return data

    def extract_tweet_quote_retweets(self, tweet_url):
        # Creates a new (unauthenticated) driver to visit the tweet page and extract the quote retweets
        qr_driver=webdriver.Edge()
        qr_driver.get(tweet_url)
        time.sleep(15)
        tweet=qr_driver.find_element(By.CSS_SELECTOR, "article[data-testid='tweet']")
        tweet_quote_retweets=tweet.find_elements(By.CSS_SELECTOR, "span[data-testid='app-text-transition-container']")[1].text or "0"
        return tweet_quote_retweets

    def visit_trending_topics(self):
        # Go to each trending topic page and extract the tweets
        data = dict()
        for i in range(0, 5):
            trending_widget=self.driver.find_element(By.CSS_SELECTOR, "div[aria-label='Timeline: Trending now']")
            topic=trending_widget.find_elements(By.CSS_SELECTOR, "div[role='link']")[i]
            topic_name = topic.find_element(By.TAG_NAME, "div").find_elements(By.TAG_NAME, "div")[2].text
            topic.click()
            time.sleep(3)
            tweet_data = self.extract_tweet_data()
            data[topic_name] = tweet_data
            self.driver.back()
            time.sleep(2)
        return data
    
    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    


    ## Create custom run function for your own use case
    # Use case for scraping trending topics (strand 2)
    def run_scrape_trending(self):
        self.login_to_twitter(self.username, self.password)
        data = self.visit_trending_topics()
        
        # store the data in a csv file
        output_file = "./TrendingTopic/Data/" + self.tag + " - " + str(datetime.datetime.now()) + ".csv"
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Topic", "Tag", "Tweet", "Replies", "Retweets", "Likes", "Quote Retweets", "Sentiment Score", "Sentiment"])
            for topic in data:
                for tweet in data[topic]:
                    writer.writerow([topic, self.tag, *tweet])
        return data
    
    # Sample use case for home feed
    def run_scrape_homefeed(self):
        self.login_to_twitter(self.username, self.password)
        data = self.extract_tweet_data()
        
        # store the data in a csv file
        output_file = "./HomeFeed/Data/" + self.tag + " - " + str(datetime.datetime.now()) + ".csv"
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Tweet", "Reply", "Retweet", "Like", "Quote Retweet", "Sentiment Score", "Sentiment"])
            for row in data:
                writer.writerow(row)
        return data

if __name__ == '__main__':
    scraper = TwitterScraper("@Memes2117", "Test1234", "Test")
    scraper.run_scrape_homefeed()
    # print(scraper.run_scrape_trending())
    


