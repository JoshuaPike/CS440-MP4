"""
Part 3: Here you should improve viterbi to use better laplace smoothing for unseen words
This should do better than baseline and your first implementation of viterbi, especially on unseen words
"""
import math
def viterbi_2(train, test):
    '''
    input:  training data (list of sentences, with tags on the words)
            test data (list of sentences, no tags on the words)
    output: list of sentences with tags on the words
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''
    transDict = {}
    emissionDict = {}
    tagDict = {}
    wordDict = {}
    totalPair = 0 # I think this is needed to smooth transProb
    uniqueWord = {}
    hapaxWords = {}
    hapaxCount = {}
    tagPairFreq = {}

    
    for sentance in train:
        second = False
        prevTag = 'START'

        for pair in sentance:
            # Count tag
            if pair[1] not in tagDict:
                tagDict[pair[1]] = 1
            else:
                tagDict[pair[1]] += 1

            # Unique words per tag
            if pair[1] not in uniqueWord:
                uniqueWord[pair[1]] = {pair[0]: 1}
            elif pair[0] not in uniqueWord[pair[1]]:
                uniqueWord[pair[1]] = {pair[0]: 1}

            # Setup hapax dict
            if pair[0] not in hapaxWords and pair[0] not in wordDict:
                hapaxWords[pair[0]] = {pair[1]: 1}
                if pair[1] not in hapaxCount:
                    hapaxCount[pair[1]] = 1
                else: 
                    hapaxCount[pair[1]] += 1
            elif pair[0] in hapaxWords and pair[1] not in hapaxWords[pair[0]]:
                hapaxWords[pair[0]] = {pair[1]: 1}
                if pair[1] not in hapaxCount:
                    hapaxCount[pair[1]] = 1
                else: 
                    hapaxCount[pair[1]] += 1
            elif pair[0] in hapaxWords and pair[1] in hapaxWords[pair[0]]:
                del hapaxWords[pair[0]]
                hapaxCount[pair[1]] -= 1
                if hapaxCount[pair[1]] == 0:
                    del hapaxCount[pair[1]]

            if pair[0] not in wordDict:
                wordDict[pair[0]] = 1
            else:
                wordDict[pair[0]] += 1

            # Secodary way to do emission dict
            if pair not in emissionDict:
                emissionDict[pair] = 1
            else:
                emissionDict[pair] += 1
            
            # Count tag pairs starting at second position
            if second:
                totalPair += 1
                if (pair[1], prevTag) not in transDict:
                    transDict[(pair[1], prevTag)] = 1
                else:
                    transDict[(pair[1], prevTag)] += 1
                # if pair[1] not in tagPairFreq:
                #     tagPairFreq[pair[1]] = {prevTag: 1}
                # elif prevTag not in tagPairFreq[pair[1]]:
                #     tagPairFreq[pair[1]] = {prevTag: 1}
                # else:
                #     tagPairFreq[[pair[1]]][prevTag] += 1
            
            # Check if start so we know to start calculating transition
            if pair[0] == 'START':
                second = True
            prevTag = pair[1]

    # Trans, emission should be counted 
    transProb = {}
    emissionProb = {}
    em_smooth = 0.00005
    hapax_smooth = 0.000001
    trans_smooth = 6.5


    # Secondary way to calc emission prob
    # for pair in emissionDict:
    #     # emissionProb[pair] = math.log( (emissionDict[pair] + em_smooth) / (tagDict[pair[1]] + em_smooth*(len(tagDict) + 1)) )
    #     if pair[0] in hapaxWords:
    #         emissionProb[pair] = math.log( (emissionDict[pair] + hapax_smooth) / (tagDict[pair[1]] + hapax_smooth*(len(uniqueWord[pair[1]]) + 1)) )
    #     else:
    #         emissionProb[pair] = math.log( (emissionDict[pair] + em_smooth) / (tagDict[pair[1]] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )
    # for tag in tagDict:
    #     # emissionProb[('UNKNOWN', tag)] = math.log( em_smooth / (tagDict[tag] + em_smooth*(len(tagDict) + 1)) )
    #     emissionProb[('UNKNOWN', tag)] = math.log( em_smooth / (tagDict[tag] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )

    for word in wordDict:
        for tag in tagDict:
            # if tag == 'START' or tag == 'END':
                # continue
            pair = (word, tag)
            if pair in emissionDict:
                # Check if hapax word
                # if word in hapaxWords:
                #     scale = hapaxCount[tag]/len(hapaxWords)
                emissionProb[pair] = math.log( (emissionDict[pair] + em_smooth) / (tagDict[pair[1]] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )
                # else:
                #     emissionProb[pair] = math.log( (emissionDict[pair] + em_smooth) / (tagDict[pair[1]] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )
            # elif word in wordDict:
            #     emissionProb[pair] = math.log(0.000000001)
            # else:
                # emissionProb[('UNKNOWN', tag)] = math.log( em_smooth / (tagDict[tag] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )
            if tag in hapaxCount:
                scale = hapaxCount[tag]/len(hapaxWords)
                emissionProb[('UNKNOWN', tag)] = math.log( scale*em_smooth / (tagDict[tag] + scale*em_smooth*(len(uniqueWord[pair[1]]) + 1)) )
            else:
                emissionProb[('UNKNOWN', tag)] = math.log( em_smooth / (tagDict[tag] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )


    # find transition prob
    for tagA in tagDict:
        for tagB in tagDict:
            tagPair = (tagA, tagB)
            # if tagPair in transDict:
            #     transProb[tagPair] = math.log(transDict[tagPair] / totalPair)
            # else:
            #     transProb[tagPair] = math.log(0.000000000000001)
            if tagPair in transDict:
                
                transProb[tagPair] = math.log((transDict[tagPair] + trans_smooth) / (totalPair + trans_smooth*(tagDict[tagB] + 1)))
            else:
                transProb[tagPair] = math.log((trans_smooth) / (totalPair + trans_smooth*(tagDict[tagB] + 1)))

    # Viterbi algorithm
    toRet = []

    for sentance in test:
        # V is list of dictionaries... each of with hold a tag key and value
        v = []
        # Have b hold {current tag: previous tag}
        b = []

        # Fill in first column
        # HAS TRANSITION PROB FROM START TO TAG MIGHT BE WRONG
        firstCol = {}
        for tag in tagDict:
            word = sentance[1]
            if (word, tag) in emissionProb:
                temp = transProb[(tag, 'START')] + emissionProb[(word, tag)]
            else:
                temp = transProb[(tag, 'START')] + emissionProb[('UNKNOWN', tag)]
            firstCol[tag] = temp
        v.append(firstCol)
        # Line below could fuck shit up
        b.append('START')

        # for loop from the second real word to 'END'
        for k in range(1, len(sentance)):
            # k is the "k + 1" in notes... plug in k-1 for v
            word = sentance[k]
            # column to add to v
            vColToAdd = {}
            # column to add to b
            bColToAdd = {}

            # Handle non end cases
            if word != 'END':
                # for each tagB...
                for tagB in tagDict:
                    # maxArr is array used to store all possible calc before taking max
                    maxArr = []
                    # for each tagA...
                    for tagA in tagDict:
                        # check if word, tag is in emission
                        transProb[(tagB, tagA)]
                        if (word, tagB) in emissionProb:
                            maxArr.append( (v[k-1][tagA] + transProb[(tagB, tagA)] + emissionProb[(word, tagB)], tagA) )
                        else:
                            maxArr.append( (v[k-1][tagA] + transProb[(tagB, tagA)] + emissionProb[('UNKNOWN', tagB)], tagA) )
                    vColToAdd[tagB] = max(maxArr)[0]
                    bColToAdd[tagB] = max(maxArr)[1]
                v.append(vColToAdd)
                b.append(bColToAdd)
            else:
                # Handle end cases
                # tagB can only be 'END' now... word = 'END'
                tagB = 'END'
                maxArr = []

                for tagA in tagDict:
                    
                    # Don't think i need to have this pair check but here for saftey
                    if (word, tagB) in emissionProb:
                        maxArr.append( (v[k-1][tagA] + transProb[(tagB, tagA)] + emissionProb[(word, tagB)], tagA) )
                    else:
                        maxArr.append( (v[k-1][tagA] + transProb[(tagB, tagA)] + emissionProb[('UNKNOWN', tagB)], tagA) )
                v.append({'END': max(maxArr)[0]})
                b.append({'END': max(maxArr)[1]})
        
        # At this point the b matrix should be good
        toAdd = []
        curTag = b[len(sentance) - 1]['END']
        toAdd.append(('END', 'END'))
        for i in reversed(range(1, len(sentance) - 1)):
            word = sentance[i]
            toAdd.append((word, curTag))
            curTag = b[i][curTag]
        toAdd.append(('START', 'START'))
        toAdd.reverse()
        toRet.append(toAdd)
            
    return toRet