"""
Part 1: Simple baseline that only uses word statistics to predict tags
"""
import operator
def baseline(train, test):
    '''
    input:  training data (list of sentences, with tags on the words)
            test data (list of sentences, no tags on the words)
    output: list of sentences, each sentence is a list of (word,tag) pairs.
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''
    # For each word w, count how many times w occurs with each tag
    # When processing the test data, it consistently gives w the tag that was seen most often
    # For unseen words, it should guess the tag that's seen the most often in training dataset
    tagDict = {}
    wordDict = {}
    # Set up dicts
    for sentance in train:
        for pair in sentance:
            # Check if word, tag pair in word dict
            if pair[0] != 'START' and pair[0] != 'END':
                if pair[0] not in wordDict:
                    wordDict[pair[0]] = {pair[1]: 1}
                elif pair[1] not in wordDict[pair[0]]:
                    wordDict[pair[0]][pair[1]] = 1 
                else:
                    wordDict[pair[0]][pair[1]] += 1
                
            # Check if tag in tagDict
            if pair[1] not in tagDict:
                tagDict[pair[1]] = 1
            else:
                tagDict[pair[1]] += 1
    # Get most common tag
    commonTag = max(tagDict, key=tagDict.get)
    toRet = []
    
    for sentance in test:
        toAdd = []
        for word in sentance:
            if word in wordDict:
                toAdd.append((word, max(wordDict[word], key=wordDict[word].get)))
            else:
                toAdd.append((word, commonTag))
        toRet.append(toAdd)

    return toRet