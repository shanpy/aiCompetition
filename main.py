import json
import csv
import helpers
import time
import get_tweets
import compareName


def compare_process(acct, acct_name):
    #compare first_acct and remove semantic similarities
    print('Start to remove similarities at ' + acct_name)

    new_collect = []
    with open('%s_tweets.csv' % acct_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["number", "created_at", "text"])
    for index, fa in enumerate(acct):
        results = helpers.hammingCompare(acct, acct.pop())
        for result in results:
            try:
                new_collect.append(result)
                writer.writerow('{}{}{}'.format(result))
                del(first_acct, result[0])
            except Exception as e:
                pass
    pass
    return new_collect

def main_compare(first_acct, second_acct):

        new_collect_1 = compare_process(first_acct, compareName.firstAccount)
        new_collect_2= compare_process(second_acct, compareName.secondAccount)
        with open('%s_tweets.csv' % acct_name, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["number", compareName.firstAccount, compareName.secondAccount])
            for index, nc2 in enumerate(new_collect_2):
                results = helpers.hammingCompare(new_collect_1, nc2)
                for result in results:
                    try:
                        writer.writerow('{}{}{}'.format(result))
                        del(new_collect_1, result[0])
                    except Exception as e:
                        pass
        pass

        #_acct is a list with [tweet.id_str, tweet.created_at, tweet_content] format
        # for index, sa in enumerate(second_acct):
        #         print("Start comparing tweet " + str(index) + " at " + '{%H:%M:%S}'.format(datetime.datetime.now()))
        #         results = helpers.hammingCompare(first_acct, sa[2])
        #         print("Finish comparing tweet " + str(index) + " at " + '{%H:%M:%S}'.format(datetime.datetime.now()))
        #         #write each row
        #         for result in results:
        #             try:
        #                 writer.writerow('{}{}{}'.format(result))
        #                 del(first_acct, result[0])
        #             except Exception as e:
        #                 pass



if __name__ == '__main__':
        second_acct = get_tweets.get_all_tweets(compareName.secondAccount)
        first_acct = get_tweets.get_all_tweets(compareName.firstAccount)
        if (not type(second_acct[0][2]) is bool) and (not type(first_acct[0][2]) is bool):
            main_compare(first_acct, second_acct)
            print("Please check compareName_tweets.csv for final result")
        else:
            print(str(second_acct[0][1]) + " " + str(first_acct[0][1]))
