import os
import json
from bs4 import BeautifulSoup
import sys
import nltk
from nltk.tokenize import word_tokenize
#nltk.download('punkt')

import nltk
from nltk.stem.snowball import SnowballStemmer,PorterStemmer
from krovetzstemmer import Stemmer

'''
install instructions - 
1) pip3 install nltk
2) execute line 7 in a python script
3) pip3 install krovetzstemmer
'''




#We are going to try Krovetz stemmer, Porter stemmer ,snowballstemmer and lemmatization to compare performance

def writeDictToFile(wordDictionary):

    
    with open("./results/wordDictionaryData.txt", "w") as file: 

        for word in wordDictionary:

            file.write(word + " " + str(wordDictionary[word]) + "\n")

        print("Data successfully written")

    return


class Indexer():
    
    index = {}
    currFile = ''

    def __init__(self,path="./developer/DEV/",stemmer="krovetz"):
        self.path = path
        self.stemmer = stemmer
        return
    

    def write_index_to_file(self):
        json_object = json.dumps(self.index, indent = 8) 

        with open("TotalIndex.json", "w") as outfile:
            outfile.write(json_object)
        
        return


    def read_index_to_file(self):
        return

    def compute_tf_idf_score(self):
        return -1

    def addToIndex(self,word):
        #Each token/word needs to have a list of documents that it is present in along with the tf-idf score.
        if(word not in self.index.keys()):
            self.index[word] = []

        new_entry = [self.currFile,self.compute_tf_idf_score()]
        self.index[word].append(new_entry)
        return

    def displayIndex(self):
        for word in self.index:
            print("The word is " + word + " and the list is ")
            print(self.index[word])
            print()
        return

    def Stemming(self,words):
        stem_words = []
        if(self.stemmer == "porter"):
            porter_stemmer = PorterStemmer()
            for w in words:
                stemmedWord = porter_stemmer.stem(w)
                stem_words.append(stemmedWord)
                self.addToIndex(stemmedWord)


        elif(self.stemmer == "snowball"):
            snow_stemmer = SnowballStemmer(language='english')
            for w in words:
                stemmedWord = snow_stemmer.stem(w)
                stem_words.append(stemmedWord)
                self.addToIndex(stemmedWord)

        else:
            #print("Using Default Stemmer")
            krovetz_stemmer = Stemmer()
            for w in words:
                stemmedWord = krovetz_stemmer.stem(w)
                stem_words.append(stemmedWord)
                self.addToIndex(stemmedWord)

        return stem_words

    def localParser(self):
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                #print(os.path.join(root, name))
                # Opening JSON file
                self.currFile = name
                f = open(os.path.join(root, name))

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
                
                #for e1,e2 in zip(words,stem_words):
                #        print(e1+' ----> '+e2)

                self.displayIndex()
                sys.exit(0)

        return

if __name__ == "__main__":
    idx = Indexer()
    idx.localParser()