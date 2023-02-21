import os
import json
from bs4 import BeautifulSoup
import sys
import nltk
from nltk.tokenize import word_tokenize
#nltk.download('punkt')

import nltk
from nltk.stem.snowball import SnowballStemmer,PorterStemmer
 

#We are going to try Krovetz stemmer, Porter stemmer ,snowballstemmer and lemmatization to compare performance

class Indexer():
    
    index = {}
    def __init__(self,path="./developer/DEV/",stemmer="snowball"):
        self.path = path
        self.stemmer = stemmer
        return
    
    def Stemming(self,words):
        stem_words = []
        if(self.stemmer == "porter"):
            porter_stemmer = PorterStemmer()
            for w in words:
                stemmedWord = porter_stemmer.stem(w)
                stem_words.append(stemmedWord)

        else:
            #print("Using Default Stemmer")
            snow_stemmer = SnowballStemmer(language='english')
            for w in words:
                stemmedWord = snow_stemmer.stem(w)
                stem_words.append(stemmedWord)

        return stem_words

    def localParser(self):
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                #print(os.path.join(root, name))
                # Opening JSON file
                f = open((os.path.join(root, name)))

                b_raw = json.load(f)
                html = b_raw["content"]
                soup = BeautifulSoup(html, "html.parser")
            
                for data in soup(['style', 'script','a']):
                    # Remove tags
                    data.decompose()
            
                # return data by retrieving the tag content
                alltxtcontent = ' '.join(soup.stripped_strings)

                #print(alltxtcontent)
                words = word_tokenize(alltxtcontent.lower())
                stem_words = self.Stemming(words)
                #print(words)
                #stem's of each word
                
                for e1,e2 in zip(words,stem_words):
                        print(e1+' ----> '+e2)

                sys.exit(0)

        return

if __name__ == "__main__":
    idx = Indexer()
    idx.localParser()