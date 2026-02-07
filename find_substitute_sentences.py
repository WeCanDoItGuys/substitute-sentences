"""Created on Fri Jan  9 19:18:26 2026"""

from collections import defaultdict
import os
from datetime import datetime
#Finds phrases that a test phrase can substitute cipher into.

# start with word that has fewest candidates
#   for each candidate, shrink the other words' candidate lists, and check the one with shortest, recursively
# along the way store candidates what have letters in a given position

#Lowercase and remove nonalpha # Hi 1 -> hi
letter_set = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
deletions = ''.join(ch for ch in map(chr,range(256)) if ch not in letter_set)
table = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz', deletions)
def lower_alpha(s):
    return s.translate(table)

#Apply substitution #sheep -> ABCCD
def standardize(w):
    subs={' ':' '}
    sub=65 #ord('A')
    for char in w:
        if char not in subs:
            subs[char]=chr(sub)
            sub+=1
    return ''.join(subs[char] for char in w)

#Test all words
def find_substitutes(test_sentence):
    #test_sentence='be the Change you want to see in the World'
    #capitalize words you don't want in the substitution
    test_words=test_sentence.split()
    if len(test_words)==0: return []
    dont_selfsubstitute={word.lower() for word in test_words if word.lower()!=word}
    test_words=[word.lower() for word in test_words]
    
    #set of all words in dictionary with lengths between min and max of test words
    min_length = min(len(word) for word in test_words)
    max_length = max(len(word) for word in test_words)
    #frequent_scrabble (45k), frequent_scrabble_medium (12k), frequent_scrabble_small (3k)
    dictionary_file = '../dictionary/12dicts/International/3of6game.txt' #'12dicts/International/3of6game.txt'
    with open(dictionary_file) as f:
        words={w for word in f.read().splitlines() 
                  if min_length<=len(w:=lower_alpha(word))<=max_length}
    
    #dict of all words in dictionary with a given structure (ABCCBD: bottom vessel common etc)
    structure = defaultdict(set)
    for word in words:
        structure[standardize(word)].add(word)
    
    #dict of all words with same structure as each test word
    candidates={word: structure[standardize(word)].copy() for word in test_words}
    for word in dont_selfsubstitute: 
        candidates[word].discard(word)
    
    #dict of candidates broken up by containing a letter
    alphabet='abcdefghijklmnopqrstuvwxyz'
    d={word: {l: {c for c in candidates[word] if l in c} for l in alphabet} for word in test_words}
    cands={word: {l:{} for l in alphabet} for word in test_words}
    
    #each word in the phrase sets rules for others #'sky kayak fly'
    rules={word:{} for word in test_words}  #{'sky':{}, 'kayak':{}}
    for i, word1 in enumerate(test_words):  #[(0,'sky'), (1,'kayak')]
        letters=[l for l in dict.fromkeys(word1)] #['s','k','y'] 
                 #if all(l not in w for w in test_words[:i])] #dont rerule letters #MUST MOVE TO WITHIN LOOP
        for letter in letters:                   #[(0,'s'),(1,'k'),(2,'y')]
            rules[word1][word1.find(letter)]=\
                {word2: word2.find(letter)       #first position of 's' in kayak
                 for word2 in test_words}        #rules['sky'][0]['kayak'] = -1
    
    def follow_rules(cs, w1, w2, c1):
        '''Subset of cs that have letters of c1 in positions required by w1 in w2'''
        for l in rules[w1]:
            letter=c1[l]
            pos=rules[w1][l][w2]
            cs &= cands[w2][letter].setdefault(pos, 
                  candidates[w2] - d[w2][letter] if pos==-1 else
                  {w for w in d[w2][letter] if w[pos]==letter})
    
    def sort_sets(remaining, c1, cs, phrase):
        '''Shrink sets of candidates, sort by shortest, and update phrases'''
        if len(remaining)==0:
            phrases.append([w for i,w in sorted(phrase)])
            phrase.clear()
            return
        
        remn = remaining.copy()
        cs = {w:cs[w].copy() for w in [test_words[i] for i in remn]}
        for i in remn:
            w1 = test_words[phrase[-1][0]]
            w2 = test_words[i]
            follow_rules(cs[w2], w1, w2, c1) #apply rule of newest word in phrase to all candidate lists
        
        remn.sort(key=lambda i: len(cs[test_words[i]]))
        i_ = remn.pop(0) #smallest list gets added to phrase
        for c in cs[test_words[i_]]:
            sort_sets(remn, c, cs, phrase+[(i_,c)])
    
    phrases = []
    remn = [i for i in range(len(test_words))] #? consider removing duplicate words
    remn.sort(key=lambda i: len(candidates[test_words[i]]))
    i_ = remn.pop(0)
    for c in candidates[test_words[i_]]:
        phrase=[(i_,c)]
        sort_sets(remn, c, candidates, phrase)
    
    phrases=sorted(' '.join(phrase) for phrase in phrases)

    return phrases