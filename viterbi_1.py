"""
Part 2: This is the simplest version of viterbi that doesn't do anything special for unseen words
but it should do better than the baseline at words with multiple tags (because now you're using context
to predict the tag).
"""
import math
def viterbi_1(train, test):
    '''
    input:  training data (list of sentences, with tags on the words)
            test data (list of sentences, no tags on the words)
    output: list of sentences with tags on the words
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''
    # Markov assumptions
    # P(w_k) depends only on P(t_k)
    # P(t_k) depends only on P(t_k-1)
    # P(T | W) = P(t1 | START) * PRODSUM(1 to n) P(w_i | t_i) * PRODSUM(2 to n) P(t_k | t_k-1)
    # Count occurances of tags, tag pairs, tag/word pairs
    # Veterbi trellis only for finding highest-probability tag sequence... Only done after probabilities are found
    # Laplace smoothing
    # P(W | T) = (count + alpha) / (n + alpha(V+1))
    # P(UNK | T) = alpha / (n + alpha(V+1))
    # count = number of word given tag
    # n = number of all words given tag t
    # V = total number of tags 16

    # PROBLEMS TO FIX
    # Unseen accuracy is v low ----> Most likely emission prob
    # No it's not its transition

    # Added start/end dont know if thats correct
    transDict = {}
    emissionDict = {}
    tagDict = {}
    wordDict = {}
    totalPair = 0 # I think this is needed to smooth transProb
    uniqueWord = {}

    
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
            
            # Check if start so we know to start calculating transition
            if pair[0] == 'START':
                second = True
            prevTag = pair[1]

    # Trans, emission should be counted 
    transProb = {}
    emissionProb = {}
    em_smooth = 0.0005

    # Secondary way to calc emission prob
    for pair in emissionDict:
        # emissionProb[pair] = math.log( (emissionDict[pair] + em_smooth) / (tagDict[pair[1]] + em_smooth*(len(tagDict) + 1)) )
        emissionProb[pair] = math.log( (emissionDict[pair] + em_smooth) / (tagDict[pair[1]] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )
    for tag in tagDict:
        # emissionProb[('UNKNOWN', tag)] = math.log( em_smooth / (tagDict[tag] + em_smooth*(len(tagDict) + 1)) )
        emissionProb[('UNKNOWN', tag)] = math.log( em_smooth / (tagDict[tag] + em_smooth*(len(uniqueWord[pair[1]]) + 1)) )

    # find transition prob
    for tagA in tagDict:
        for tagB in tagDict:
            tagPair = (tagA, tagB)
            if tagPair in transDict:
                transProb[tagPair] = math.log(transDict[tagPair] / tagDict[tagB])
            else:
                transProb[tagPair] = math.log(0.000001)

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