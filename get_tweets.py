import tweepy
import re
import apiKey

######## Get Tweets and Clean
def get_all_tweets(screen_name):
 # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(apiKey.twitter_customer, apiKey.twitter_customer_secret)
    auth.set_access_token(apiKey.twitter_token, apiKey.twitter_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    print("Reading Posts from @" + screen_name + " now...")
    # make initial request for most recent tweets (200 is the maximum allowed count)
    user = api.get_user(screen_name=screen_name)
    new_tweets = api.user_timeline(screen_name=screen_name, count=50)
    # save most recent tweets
    alltweets.extend(new_tweets)
    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    try:
        while len(new_tweets) > 0:
            # all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
            # save most recent tweets
            alltweets.extend(new_tweets)
            # update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
    except Exception as e:
        return [[0,"Error in retriving timeline from @"+screen_name+":"+str(e),False]]

    try:
        # transform the tweepy tweets into a 2D array that will populate the csv
        outtweets = []
        for tweet in alltweets:
            # remove Emoji
            emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
            te = re.sub(emoji_pattern, "", tweet.text)
            tweet_content = clean_text(str(te).encode('ascii','ignore')).strip()
            if tweet_content and (not tweet_content.isspace()) and len(tweet_content)>0:
                outtweet = [tweet.id_str, tweet.created_at, tweet_content]
                outtweets.append(outtweet)
        return outtweets
    except Exception as e:
        return [[0,"Error in packing new tweets from @"+screen_name+":"+str(e),False]]


def clean_text(twitter_text):
    before_http = re.sub('https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)','',str(twitter_text))
    no_b = before_http.replace('b\'RT', '').replace('\'b', '').replace('RT','').replace('b\'','').replace('\'','')
    no_at = no_b.replace('@', '')
    no_hashtag = re.sub('/^@(.*?)\s/','', no_at)
    return no_hashtag.replace('/n','')
