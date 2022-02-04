import copy
#from WordleAssistant import WordleAssistant
from WordleLib import WordleAssistant


class WordleAssistant2(WordleAssistant):
    """
    Upgraded wordle assistant also considering letter prevalence distribution at the
    letter positions.
    
    """
    def __init__(self, size: int = 5, dictionary : str = None ):
        super().__init__(size, dictionary)
        self.FullLettPrevSite = self._letterDistSite(self.FullWorddict)
        self.CurLettPrevSite = copy.deepcopy(self.FullLettPrevSite)
        
    def initWordMeasure(self):
        """
        As the wordscore calculation will depend on the child class, 
        this can not be placed in the __init__ as issues arise with the implementation:
            incorrect overriding in different locations.
        """
        self._calcScore(self.FullWorddict,self.FullLettPrev)
        self.CurWorddict = copy.deepcopy(self.FullWorddict)
        
    def _letterDistSite(self, WD: dict)->list:
        """
        Return a list of sorted lists of tuples.
        --> first index: letter position,
        --> second index:  the letter 
        --> value:  the fraction
        
        Parameter:
            - WD : The worddict (Full or current) of the WordleAssistant for which the letter 
                    distribution is calculated.
                    
        Return list of [dicts of wordfraction (0<=x<=1)]
        """
        keys = list('abcdefghijklmnopqrstuvwxyz')
        abc = [dict.fromkeys(keys,0) for i in range(self.WordleSize)]
        numwords = len(WD)
        for key in WD:
            word = WD[key]['letters']
            for i in range(self.WordleSize):
                c = word[i]
                abc[i][c] +=1
            
        for i in range(self.WordleSize):
            for l in keys:
                abc[i][l] = float(abc[i][l])/numwords
                
        return abc
    
    def _calcScore(self, WD:dict, LP:list):
        """
        Calculate the score of each word in the WD word-dict using the LP letterprevalence.
        
        Note that the prevalence is set to one if the letter is present in the word.
        
        Parameters:
            - WD : The worddict (Full or current) of the WordleAssistant for which the scores 
                    are calculated.
            - LP : The associated Letter prevalence list of tuples. (Full or current)
        """
        #print("Calculate New Score")
        for key in WD:
            WD[key]['score'] = 0 # reset the scores
            for i in range(self.WordleSize):
                WD[key]['score'] += self.CurLettPrevSite[i][WD[key]['letters'][i]]
            
    
    def reset(self):
        """
        Reset the "Current" attributes back to the "Full" attributes.
        """
        super().reset()
        #copies to start from and which will be updated every round
        keys = list('abcdefghijklmnopqrstuvwxyz')
        self.CurLettPrevSite = [dict.fromkeys(keys,0) for i in range(self.WordleSize)]
        for i in range(self.WordleSize):
            for l in keys:
                self.CurLettPrevSite[i][l] = self.FullLettPrevSite[i][l]
        
        
        
        