import tweepy
import re
import compareName
import retinasdk
import apiKey
import textdistance
import json
import csv
import simhash


######## Get Tweets and Clean

def get_all_tweets(screen_name):
 # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(apiKey.twitter_customer, apiKey.twitter_customer_secret)
    auth.set_access_token(apiKey.twitter_token, apiKey.twitter_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # try:
    # start
    print("Reading Posts from @" + screen_name + " now...")
    # make initial request for most recent tweets (200 is the maximum allowed count)
    user = api.get_user(screen_name=screen_name)
    new_tweets = api.user_timeline(screen_name=screen_name, count=50)
    # save most recent tweets
    alltweets.extend(new_tweets)
    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
        # keep grabbing tweets until there are no tweets left to grab
    # except Exception as e:
    #     return [[0,"Error in initialize new tweets from @"+screen_name+":"+str(e),False]]

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
            if tweet_content and (not tweet_content.isspace()):
                outtweet = [tweet.id_str, tweet.created_at, tweet_content]
                outtweets.append(outtweet)

        # write the csv
        # with open('%s_tweets.csv' % screen_name, 'w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(["id", "created_at", "text"])
        #     writer.writerows(outtweets)
        # pass
        return outtweets
    except Exception as e:
        return [[0,"Error in packing new tweets from @"+screen_name+":"+str(e),False]]


def clean_text(twitter_text):
    before_http = re.sub('https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)','',str(twitter_text))
    no_b = before_http.replace('b\'RT', '').replace('\'b', '').replace('RT','').replace('b\'','').replace('\'','')
    no_at = no_b.replace('@'+compareName.firstAccount+':', '').replace('@'+compareName.secondAccount+':', '').replace('@',' ')
    no_hashtag = re.sub('/^@(.*?)\s/','', no_at)
    return no_hashtag.replace('/n','')





######### Semantic Similarity Check

def compare(outtweets, innerTwitter):
    #init
    client = retinasdk.FullClient(apiKey.retina_token, apiServer="http://api.cortical.io/rest", retinaName="en_associative")
    liteClient = retinasdk.LiteClient(apiKey.retina_token)
    res = [];

    ##outtweet is a list with [tweet.id_str, tweet.created_at, tweet_content] format
    for outtweet in outtweets:
        result = {}

        # hamming_result= hammingCompare(outtweet[2], innerTwitter)
        # if hamming_result[0]:
        #     result["hamming"] = hamming_result[0][0]

        # retrive keyword & re-constrct
        # keyword_sentense = keywordRetrive(outtweet[2], innerTwitter, liteClient)
        # if keyword_sentense["out_keywords"]:
        #     hamming_result_keyword = hammingCompare(keyword_sentense["out_keywords"], keyword_sentense["inner_keywords"])
        #     result["hamming_keyord"] = hamming_result_keyword[0][0]

        # get simHash
        simhash_pair = getSimHash(outtweet[2], innerTwitter, client)
        if len(simhash_pair)>1:
            diff_bits = simhash.num_differing_bits(simhash_pair['out_hash'], simhash_pair['in_hash'])

            hashes = [simhash_pair['out_hash'], simhash_pair['in_hash']]

            # Number of blocks to use (more in the next section)
            blocks = 4
            # Number of bits that may differ in matching pairs
            distance = 3
            matches = simhash.find_all(hashes, blocks, distance)
            res.append([outtweet[2],matches])
    return res


# keyword Retrive
def keywordRetrive(outtweet, innerTwitter, liteClient):
    try:
        out_keywords = liteClient.getKeywords(outtweet)
        inner_keywords = liteClient.getKeywords(innerTwitter)
        print("Keywords from @"+compareName.firstAccount+":"+out_keywords)
        print("Keywords from @"+compareName.secondAccount+":"+innerTwitter)
        return {"out_keywords": ''.join(out_keywords), "inner_keywords": ''.join(inner_keywords)}
    except Exception as e:
        return {"out_keywords": False}


# simHash & Hamming Distance
def hammingCompare(outtweet, innerTwitter):
    print("checking ' " + outtweet + " ' now...")
    least_hamming = 100
    least_hamming_tweet = ""
    hamming_dis = textdistance.hamming.distance(outtweet, innerTwitter)
    # ask hamming distance <10
    if hamming_dis < least_hamming <= 10:
        least_hamming = hamming_dis
        least_hamming_tweet = outtweet
        return [True, [least_hamming, least_hamming_tweet]]
    else:
        return [False, least_hamming]


def getSimHash(outtweet, innerTwitter, client):
    try:
        fingerprints = getFingerPrint(outtweet,innerTwitter, client)
        if len(fingerprints)>1:
            out_hash = simhash.compute(fingerprints["out_fingerprint"])
            in_hash = simhash.compute(fingerprints["inner_fingerprint"])
            return {'out_hash':out_hash, 'in_hash':in_hash}
        else:
            return {'out_hash':False}
    except Exception as e:
        return {'out_hash':False}


def getFingerPrint(outtweet, innerTwitter, client):
    try:
        print("working on :" + str(outtweet))
        first_fingerprint = client.getFingerprintForText(str(outtweet)).positions
        second_fingerprint = client.getFingerprintForText(str(innerTwitter)).positions
        return {"out_fingerprint": first_fingerprint, "inner_fingerprint": second_fingerprint}
    except Exception as e:
        return {'out_hash':False}


if __name__ == '__main__':
    # pass in the username of the account you want to download
    second_acct = get_all_tweets(compareName.secondAccount)
    first_acct = get_all_tweets(compareName.firstAccount)
    if (not type(second_acct[0][2]) is bool) and (not type(first_acct[0][2]) is bool):
        for sa in second_acct:
                results = compare(first_acct, sa[2])
                for result in results:
                    print(result[0]+" is similar to " + sa[2])
    else:
        print(str(second_acct[0][1]) + " " + str(first_acct[0][1]))
