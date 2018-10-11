import tweepy
import csv
import compareName
import retinasdk
import apiKey
import textdistance


######## Get Tweets and Clean

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
    except Exception as e:
        return [[0,"Error in initialize new tweets from @"+screen_name+":"+str(e),False]]

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
            tweet_content = clean_text(tweet.text).strip()
            if tweet_content and (not tweet_content.isspace()):
                outtweet = [tweet.id_str, tweet.created_at, tweet_content]
                outtweets.append(outtweet)

        # write the csv
        with open('%s_tweets.csv' % screen_name, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "text"])
            writer.writerows(outtweets)
        pass      
        return outtweets
    except Exception as e:
        return [[0,"Error in packing new tweets from @"+screen_name+":"+str(e),False]]


def clean_text(twitter_text):
    before_http = str(twitter_text).split("https://")[0]
    no_b = before_http.replace('b\'RT', '').replace('\'b', '').replace('RT','').replace('b\'','').replace('\'','')
    no_at = no_b.replace('@'+compareName.firstAccount+':', '').replace('@'+compareName.secondAccount+':', '')
    return no_at





######### Semantic Similarity Check

def compare(outtweets, innerTwitter):
    for outtweet in outtweets:
        hamming_result = hammingCompare(outtweet, innerTwitter)
        fingeprint_result = rake_client(outtweet, innerTwitter)["fingerprint"]
        if (hamming_result[0]) or (fingeprint_result>=1):
            return {"tweet content": outtweet, "hamming":hamming_result, "fingerprint": fingeprint_result}
        else:
            return False

# simHash & Hamming Distance
def hammingCompare(outtweet, innerTwitter):
    least_hamming = 10000000
    least_hamming_tweet = ""
    hamming_dis = textdistance.hamming.distance(outtweet[2], innerTwitter[2])
    # ask hamming distance <1000
    if hamming_dis < least_hamming < 1000:
        least_hamming = hamming_dis
        least_hamming_tweet = outtweet[2]
        return [True, [least_hamming, least_hamming_tweet]]
    else:
        return [False, least_hamming]


def rake_client(outtweet, innerTwitter):
    client = retinasdk.FullClient(apiKey.retina_token, apiServer="http://api.cortical.io/rest", retinaName="en_associative")
    first_fingerprint = client.getFingerprintForText(outtweet)
    print(first_fingerprint)
    second_fingerprint = client.getFingerprintForText(innerTwitter)
    fingerprint_res = client.compare(first_fingerprint,second_fingerprint )
    # keywords_outtweet = liteClient.getKeyword(outtweet)
    return {"fingerprint": fingerprint_res}


if __name__ == '__main__':
    # pass in the username of the account you want to download
    second_acct = get_all_tweets(compareName.secondAccount)
    first_acct = get_all_tweets(compareName.firstAccount)
    if (not type(second_acct[0][2]) is bool) and (not type(first_acct[0][2]) is bool): 
        for sa in second_acct:
                result = compare(first_acct, sa)
                if isinstance(result, dict):
                    print("@" + compareName.secondAccount+": " + sa + " has similar tweet from @"+compareName.firstAccount)
                    for method,res in result.items():
                        print(str(method)+": " + str(res))
                    # else:
                    # print("Hamming distance too large: " + str(hammingResult[1]))
    else:
        print(str(second_acct[0][1]) + " " + str(first_acct[0][1]))
