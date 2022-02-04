import copy, os


class WordleAssistant():
    """
	The WordleAssistant class provides access to the dictionary and measures
	of quality for each (remaining) word with regard to its possibility of being
	the wordle.
	
	Attributes:
	  - WordleSize : size of the wordle words (int, default=5 )
      - FullSize : Total size of the set of words ol length wordlesize
	  - CurSize : Number of possible remaining words (int)
	  - FullWordset : set containing all the words
	  - FullWorddict: dictionary with the words
	  - FullLettPrev: list with tuple-pairs (letter:count)
      - CurWordset  : set containing all the words
	  - CurWorddict : dictionary with the words
      - CurLettPrev : dictionary with lettercount for retained words
	  - LetterStatus: dictionary of alphabet linked to values 
                      * -1(no clue), 
                      *  0(not in there), 
                      *  1(in there somewhere),
                      *  2(we know an exact position)
	  - FoundLetters: dict of lists. Key=letter which is in the word, list with all positions; -1: not checked, 0: wrong position, 1: correct position
	"""
    def __init__(self, size: int = 5, dictionary : str = None ):
        """
        Initialize the WordleAssistant by reading a dictionary and selecting all words of a given size.
        
        Parameters:
            - size : length of wordle words
            - dictionary : string with the adress of the dictionary [default: words.txt (113k dictionary)]
		
        """
        #print("Did I init OLD?")
        if dictionary is None:
            dictionary = os.path.join(os.path.dirname(__file__),'words.txt')
            
        self._readDict(size, dictionary)
        self.WordleSize = size
        self.FullLettPrev = self._letterDist(self.FullWorddict)
        #copies to start from and which will be updated every round
        self.CurSize = self.FullSize
        self.CurLettPrev = copy.deepcopy(self.FullLettPrev)
        self.CurWordset = copy.deepcopy(self.FullWordset)
        #keeping track of the used letters
        keys = list('abcdefghijklmnopqrstuvwxyz')
        self.LetterStatus = dict.fromkeys(keys,-1) #-1 we have no clue, 0 not present, 1 present but no correct position yet, 2 at least one correct position found
        self.FoundLetters = dict() # key=good letter, value is list of positions, with 0=wrong,1=good,-1=no clue
     
    def initWordMeasure(self):
        """
        As the wordscore calculation will depend on the child class, 
        this can not be placed in the __init__ as issues arise with the implementation:
            incorrect overriding in different locations.
        """
        self._calcScore(self.FullWorddict,self.FullLettPrev)
        self.CurWorddict = copy.deepcopy(self.FullWorddict)
        
    #use single underscore, then childclasses can overwrite it...with double they can not.
    def _readDict(self, size: int, dictionary : str):
        """
        Read a full dictionary and retain the words with the required length.
        
        Parameters:
            - size : length of the wordle words
            - dictionary : the list of words (1 per line, simple text file)
        """
        file = open(dictionary,'r')
        lines = file.readlines()
        wlist = [word.rstrip('\n') for word in lines if len(word.rstrip('\n')) == size]#need to get rid of newlines and not count them
        self.FullWordset = set(wlist)
        self.FullWorddict = dict()
        for word in wlist:
            wordProp = dict()
            wordProp['letters'] = list(word) #split the word into a list of single letters
            wordProp['chars'] = set(word)    #make a set
            wordProp['score'] = 0.0          #how good is a word as possible candidate
            self.FullWorddict[word] = wordProp
        self.FullSize = len(self.FullWordset)
        
    def _letterDist(self, WD: dict)->list:
        """
        Return a sorted list of tuples with the first element the letter and second element the fraction
        of words in the total list that contain this letter at least ones. Letters that are present multiple
        times in a word are only counted once.
        
        Parameter:
            - WD : The worddict (Full or current) of the WordleAssistant for which the letter 
                    distribution is calculated.
                    
        Return list of tuples(letter,wordfraction: 0<=x<=1)
        """
        keys = list('abcdefghijklmnopqrstuvwxyz')
        abc = dict.fromkeys(keys,0)
        
        numwords = len(WD)
        for key in WD:
            word = WD[key]
            for c in word['chars']:
                abc[c] +=1
        abcSort = sorted(abc.items(), key=lambda x:x[1], reverse=True) # largest to smallest
        return [tuple([key,float(iv)/numwords]) for key,iv in abcSort]
    
    def _calcScore(self, WD:dict, LP:list):
        """
        Calculate the score of each word in the WD word-dict using the LP letterprevalence.
        
        Note that the prevalence is set to one if the letter is present in the word.
        
        Parameters:
            - WD : The worddict (Full or current) of the WordleAssistant for which the scores 
                    are calculated.
            - LP : The associated Letter prevalence list of tuples. (Full or current)
        """
        #print("Calculate Old Score")
        LPD = dict()
        for key,val in LP:
            LPD[key]=val
        
        for key in WD:
            WD[key]['score'] = 0 # reset the scores
            for c in WD[key]['chars']:
                WD[key]['score'] += LPD[c]
                
    def getTop(self, top : int = 1)->list:
        """
        Return the Top number of words of the current wordlist based on their score, and their score.
        
        Parameters:
            - top : integer indicating how many to print. Default=10
        """
        WSlist=dict.fromkeys(self.CurWordset,0)
        
        for key in self.CurWorddict:
            WSlist[key]=self.CurWorddict[key]['score']
            
        return list(sorted(WSlist.items(), key=lambda x:x[1], reverse=True))[:top]
    
    def getScore(self, word : str)->float:
        """
        Returns a positive value reflecting the score of a word. Negative if the word is not present in the list.
        
        Parameters:
            - word : string 
        """
        if word in self.CurWordset:
            return self.CurWorddict[word]['score']
        else:
            return -1.0
    
    def getNumPos(self)->int:
        """
        Return the remaining possible number of words.
        """
        return self.CurSize
    
    def getWordset(self)->set:
        return self.CurWordset
    
    def update(self, word : str, hits : list):
        """
        Update our current wordlist and scores based on the success of a given attempt.
        
        Parameters:
            - word: string of the attempted word
            - hits: integer list with the same length as the word, giving values
                        0 = miss, 1 = wrong position, 2 = correct position
                        
        Returns +1 on success, negative values upon failure.
        """
        if not len(word)==self.WordleSize:
            print("WARNING: your word is "+str(len(word))+" letters long but should be "+str(self.WordleSize)+" letters long.")
            return -1
        if not len(hits)==self.WordleSize:
            print("WARNING: your hitlist is "+str(len(hits))+" letters long but should be "+str(self.WordleSize)+" letters long.")
            return -2
        
        for i in range(len(word)): #loop over letters
            #print("HITS_i==0 at i="+str(i)+" lettstat="+str(self.LetterStatus[word[i]])+" letter="+word[i])
            if hits[i] == 0: #letter is not in the word
                if self.LetterStatus[word[i]] == -1: #we didn't remove it yet
                    #find all words with this letter and remove them
                    self.__removeLetter(word[i])
                elif self.LetterStatus[word[i]] == 2: #the letter is correct in a different position...but wrong here (and there is no second?)  
                    #print("HITS_i==0 at i="+str(i)+" lettstat="+str(self.LetterStatus[word[i]]))
                    for j in range(self.WordleSize):
                        if self.FoundLetters[word[i]][j] == 1: # its a hit
                            self.__removeWrongPosition(j,word[i])
            if hits[i] == 1:
                if self.LetterStatus[word[i]] == -1: #we didn't see it yet
                    self.FoundLetters[word[i]] = [-1 for x in range(self.WordleSize)]
                self.FoundLetters[word[i]][i] == 0 #it's a miss
                self.__removeWrongPosition(i,word[i])
            if hits[i] == 2:
                if self.LetterStatus[word[i]] == -1: #we didn't see it yet
                    self.FoundLetters[word[i]] = [-1 for x in range(self.WordleSize)]
                
                self.FoundLetters[word[i]][i] = 1 # its a hit
                self.__removeWrongLetterAtPosition(i,word[i])
        #Update the scores & length of the list
        self._calcScore(self.CurWorddict, self.CurLettPrev)
        self.CurSize=len(self.CurWordset)
        return 1
        
    def __removeLetter(self, c : str):
        """
        Remove the letter and words containing this letter from the current lists
        
        Parameter:
            - c : string with a single character.
        """
        self.LetterStatus[c]=0
        idx = [x for x, y in enumerate(self.CurLettPrev) if y[0] == c]
        idx = idx[0]
        self.CurLettPrev[idx] = tuple([self.CurLettPrev[idx][0],0])#as tuples are immutable, they need to be fully replaced
        subset=set()
        for word in self.CurWordset:
            if c in word:
                self.CurWorddict.pop(word)
                subset.add(word)
        self.CurWordset -= subset
                                
    def __removeWrongPosition(self, i : int, c : str):
        """
        Remove the words containing this letter which is located at the wrong position 
        from the current lists and remove words missing this letter.
        
        Parameter:
            - i : integer position of the letter in the word
            - c : string with a single character.
        """
        if self.LetterStatus[c]==-1:
            self.LetterStatus[c]=1
            idx = [x for x, y in enumerate(self.CurLettPrev) if y[0] == c]
            idx = idx[0]
            self.CurLettPrev[idx] = tuple([self.CurLettPrev[idx][0],1])#as tuples are immutable, they need to be fully replaced
            
        subset=set()
        for word in self.CurWordset:
            if c not in word:#remove words missing this letter    
                self.CurWorddict.pop(word)
                subset.add(word)
            else:#remove words with this letter at the wrong position
                if word[i] == c:
                    self.CurWorddict.pop(word)
                    subset.add(word)
            
        self.CurWordset -= subset
        
    def __removeWrongLetterAtPosition(self, i : int, c : str):
        """
        Remove the words containing another letter at position i,
        as well as remove words missing this letter,
        from the current lists and remove words missing this letter.
        
        Parameter:
            - i : integer position of the letter in the word
            - c : string with a single character.
        """
        if self.LetterStatus[c] in (-1,0):
            self.LetterStatus[c]=2
            idx = [x for x, y in enumerate(self.CurLettPrev) if y[0] == c]
            idx = idx[0]
            self.CurLettPrev[idx] = tuple([self.CurLettPrev[idx][0],1])#as tuples are immutable, they need to be fully replaced
                            # we leave the prevalence at 1, will increase the score in another way
            
        subset=set()
        for word in self.CurWordset:
            if c not in word:#remove words missing this letter    
                self.CurWorddict.pop(word)
                subset.add(word)
            else:#remove words with another letter at this position
                if word[i] != c:
                    self.CurWorddict.pop(word)
                    subset.add(word)
            
        self.CurWordset -= subset
        
    def reset(self):
        """
        Reset the "Current" attributes back to the "Full" attributes.
        """
        #copies to start from and which will be updated every round
        self.CurSize = self.FullSize
        self.CurWorddict = dict()
        for key,word in self.FullWorddict.items():# ~40x faster than deep copy
            self.CurWorddict[key] = {'letters':word['letters'],
                            'chars':word['chars'],
                            'score':word['score']}
        self.CurWordset = set(self.FullWordset)       
        self.CurLettPrev = [(key,iv) for key,iv in self.FullLettPrev]
        #self.CurWorddict = copy.deepcopy(self.FullWorddict)
        #self.CurWordset = copy.deepcopy(self.FullWordset)
        #self.CurLettPrev = copy.deepcopy(self.FullLettPrev)
        #keeping track of the used letters
        keys = list('abcdefghijklmnopqrstuvwxyz')
        self.LetterStatus = dict.fromkeys(keys,-1) #-1 we have no clue, 0 not present, 1 present but no correct position yet, 2 at least one correct position found
        self.FoundLetters = dict() # key=good letter, value is list of positions, with 0=wrong,1=good,-1=no clue
    
        
        
        
        
        
        
        
        