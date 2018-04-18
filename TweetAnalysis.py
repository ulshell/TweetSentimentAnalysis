import nltk

class TweetAnalyzer():
    """Implements TweetSentimentAnalysis analysis."""

    #constructor to intialize positive and negative parameters
    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        #creating set to store postive words
        self.positives = set()

        #opening postive file in read mode
        file = open(positives, "r")
        #adding positive words in postive set()
        for line in file:
            if line.startswith(";") == False:
                self.positives.add(line.rstrip("\n"))
        #closing the file
        file.close()

        #creating set to store negative words
        self.negatives = set()
        #opening negative file in read mode
        file = open(negatives, "r")
        #adding positive words in postive set()
        for line in file:
            if line.startswith(";") == False:
                self.negatives.add(line.rstrip("\n"))
        #closing the file
        file.close()


    #function to analyze tweets
    def analyze(self, text):
        """Analyze text for TweetSentimentAnalysis, returning its score,
            by using Natural Language Toolkit functionalities.
        """

        #intializing tokenizer for tweet
        tokenizer = nltk.tokenize.TweetTokenizer()
        #obtaining only words (tokens)
        tokens = tokenizer.tokenize(text)
        s = 0
        #itterating overs words in tweets
        for word in tokens:
            if word.lower() in self.positives:
                s += 1
            elif word.lower() in self.negatives:
                s -= 1
            else:
                continue

            return s
        return 0
