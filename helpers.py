import apiKey
import retinasdk
import textdistance
import simhash

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
def hammingCompare(outtweets, innerTwitter):
    client = retinasdk.FullClient(apiKey.retina_token, apiServer="http://api.cortical.io/rest", retinaName="en_associative")
    liteClient = retinasdk.LiteClient(apiKey.retina_token)
    res = [];

    for index, outtweet in enumerate(outtweets):
        result = {}
        # get simHash
        simhash_pair = getSimHash(outtweet[2], innerTwitter, client)
        if len(simhash_pair)>1:
            diff_bits = simhash.num_differing_bits(simhash_pair['out_hash'], simhash_pair['in_hash'])
            hashes = [simhash_pair['out_hash'], simhash_pair['in_hash']]
            blocks = 4 # Number of blocks to use
            distance = 3 # Number of bits that may differ in matching pairs
            matches = simhash.find_all(hashes, blocks, distance)
            res.append([index, outtweet[2], matches])
    return res



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
        first_fingerprint = client.getFingerprintForText(str(outtweet)).positions
        second_fingerprint = client.getFingerprintForText(str(innerTwitter)).positions
        return {"out_fingerprint": first_fingerprint, "inner_fingerprint": second_fingerprint}
    except Exception as e:
        return {'out_hash':False}
