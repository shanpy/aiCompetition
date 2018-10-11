import tweepy
import csv
import compareName
import retinasdk
import apiKey
import textdistance


def get_all_tweets(screen_name):

    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(apiKey.twitter_customer, apiKey.twitter_customer_secret)
    auth.set_access_token(apiKey.twitter_token, apiKey.twitter_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    try:
        # start
        print("Reading Posts from @" + screen_name + " now...")

        # make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name=screen_name, count=200)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        # keep grabbing tweets until there are no tweets left to grab


        while len(new_tweets) > 0:
            # all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
            # save most recent tweets
            alltweets.extend(new_tweets)
            # update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1

        # transform the tweepy tweets into a 2D array that will populate the csv
        outtweets = []
        for tweet in alltweets:
            tweet_content = clean_text(tweet.text.encode("utf-8")).strip()
            if tweet_content and (not tweet_content.isspace()):
                outtweet = [tweet.id_str, tweet.created_at, tweet_content]
                outtweets.append(outtweet)

        # end
        print("Finish reading posts from @" + screen_name + " ,created at " + time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')))

        # write the csv
        with open('%s_tweets.csv' % screen_name, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "text"])
            writer.writerows(outtweets)
        pass      
        return outtweets
    except:
        return [[0,"False",False]]


def hammingCompare(outtweets, innerTwitter):
    least_hamming = 100000000000
    least_hamming_tweet = ""
    for outtweet in outtweets:
        hamming_dis = textdistance.hamming.distance(outtweet[2], innerTwitter[2])
        # ask hamming distance <10
        if hamming_dis < least_hamming < 10:
            least_hamming = hamming_dis
            least_hamming_tweet = outtweet[2]
            return [True, [least_hamming, least_hamming_tweet]]
        else:
            return [False, 0]


def clean_text(twitter_text):
    before_http = str(twitter_text).split("https://")[0]
    no_b = before_http.replace('b\'RT', '').replace('\'b', '').replace('RT','').replace('b\'','').replace('\'','')
    no_at = no_b.replace('@'+compareName.firstAccount+':', '').replace('@'+compareName.secondAccount+':', '')
    return no_at

if __name__ == '__main__':
    # pass in the username of the account you want to download
    second_acct = get_all_tweets(compareName.secondAccount)
    first_acct = get_all_tweets(compareName.firstAccount)
    print(str(second_acct[0][2]) + " " + str(first_acct[0][2]))
    if second_acct[0][2] and first_acct[0][2]: 
        for sa in second_acct:
                hammingResult = hammingCompare(first_acct, sa)
                if hammingResult[0]:
                    hamming_d = hammingResult[1][0]
                    print(str(hamming_d) + " prove: " + hammingResult[1][1] + " is similar to " + sa[2])
                else:
                    print("error occured when checking similarity of posts. Please try again")
    else:
        print("error occured when retriving posts. Please try again")
