import os
import json
from bs4 import BeautifulSoup
import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import words



#nltk.download('words')
#nltk.download('punkt')

from pathlib import Path
import nltk
from nltk.stem.snowball import SnowballStemmer,PorterStemmer
from krovetzstemmer import Stemmer

import numpy as np
'''
install instructions - 
1) pip3 install nltk
2) execute line 7 in a python script
3) pip3 install krovetzstemmer
'''




#We are going to try Krovetz stemmer, Porter stemmer ,snowballstemmer and lemmatization to compare performance

#for a given list in the indexx, the last element is going to be the tf -idf score of the element

class Indexer():
    
    index = {}
    document_to_id = {}

    currFile = ''
    docID = -1

    #doc_info = {docID,numWords in doc}
    document_info = {}

    def __init__(self,path="./developer/DEV/",stemmer="krovetz"):
        self.path = path
        self.stemmer = stemmer
        self.total_word_lst = set(w.lower() for w in nltk.corpus.words.words())
        return
    

    ''''
    #These two functions are used for testing the delta encoding to reduce space

    def addToIndex(self,word,position):
        #Each token/word needs to have a list of documents that it is present in along with the tf-idf score.
        if(word not in self.index.keys()):
            self.index[word] = []
            new_entry = [self.docID,position]
            self.index[word].append(new_entry)

        else:
            #print(self.index[word])
            if(self.index[word][-1][0]  == self.docID):  #This line is going to check the docID of the previous insertion, if same as currID then add to same list
                        self.index[word][-1].append(position)
            else:                    
                new_entry = [self.docID,position]
                self.index[word].append(new_entry)
        return

    def delta_encode(self):
        #first index of all the lists 
        #remaining all indices of the list 
        self.encodedIndex = self.index
        for word in self.index:
            for i in range(len(self.index[word])):
                for j in range(2,len(self.index[word][i])):
                    self.encodedIndex[word][i][j] -=  self.encodedIndex[word][i][j-1] 

        print()
        for word in self.encodedIndex:
            print("The word is " + word + " and the list is ")
            print(self.encodedIndex[word])
            print()

        return


    def delta_decode(self):
        self.decodedIndex = self.encodedIndex
        for word in self.encodedIndex:
            for i in range(len(self.encodedIndex[word])):
                for j in range(2,len(self.encodedIndex[word][i])):
                    self.decodedIndex[word][i][j] +=  self.encodedIndex[word][i][j-1] 

        print()
        for word in self.decodedIndex:
            print("The word is " + word + " and the list is ")
            print(self.decodedIndex[word])
            print()


        return
    '''

    def write_num_words_to_file(self):
        with open("./num_words.txt", "w") as outfile:
            outfile.write(str(len(self.index.keys())))
        return

        
    def write_document_id_to_file(self):
        json_object = json.dumps(self.document_to_id, indent = 4) 

        with open("./document_to_id.json", "a+") as outfile:
            outfile.write(json_object)
        
        self.document_to_id.clear()
        return


    def write_index_to_file(self):
        json_object = json.dumps(self.index, indent = 4) 

        with open("./TotalIndex.json", "w") as outfile:
            outfile.write(json_object)
        
        return


    def read_index_from_file(self):
        #self.displayIndex()
        self.index.clear()
        with open("./TotalIndex.json", "r") as readfile:
            self.index = json.load(readfile)

        #self.displayIndex()
        return

    def compute_tf_idf_score(self):
        print("cocmputed the tf idf score")
        #Executed at the end once the entire corpus is indexed
        for word in self.index:
            num_document_occurrences = len(self.index[word])   #Number of documents in which the word occurred

            idf = np.log((self.docID+1)/num_document_occurrences)

            #now computing tf for every document in which the word occurred
            for document in self.index[word]:
                num_occurrences_in_doc =  len(document) - 1 # -1 because the first element in the list is the docID
                num_words_in_doc = self.document_info[document[0]]
                tf = float(num_occurrences_in_doc)/num_words_in_doc
                tf_idf = tf*idf
                document.append(tf_idf)

        return 



    def addToIndex(self,word,position):
        #Each token/word needs to have a list of documents that it is present in along with the tf-idf score.
        if(word not in self.index.keys()):
            self.index[word] = []
            new_entry = [self.docID,position]
            self.index[word].append(new_entry)

        else:
            #print(self.index[word])
            if(self.index[word][-1][0]  == self.docID):  #This line is going to check the docID of the previous insertion, if same as currID then add to same list
                    #print("The length of the list is ")
                    #print(self.index[word][-1])
                    if(len(self.index[word][-1])==2):
                        self.index[word][-1].append(position)

                    else:
                        val_to_add = position - self.index[word][-1][-1]
                        self.index[word][-1].append(val_to_add)
            else:                    
                new_entry = [self.docID,position]
                self.index[word].append(new_entry)
        return

    def displayIndex(self):
        print()
        for word in self.index:
            print("The word is " + word + " and the list is ")
            print(self.index[word])
            print()
        return

    def Stemming(self,words):
        stem_words = []
        punct_lst = [",",".","?","!"]
        if(self.stemmer == "porter"):
            porter_stemmer = PorterStemmer()
            word_pos = 0
            for w in words:
                #if(not w.isalnum()):  #need to change this
                #    continue

                if(w in self.total_word_lst):
                    stemmedWord = krovetz_stemmer.stem(w)
                    stem_words.append(stemmedWord)
                    #self.addToIndex(stemmedWord,word_pos)
                    self.addToIndex(stemmedWord,word_pos)
                    word_pos += 1


        elif(self.stemmer == "snowball"):
            snow_stemmer = SnowballStemmer(language='english')
            word_pos = 0
            for w in words:
                #if(w in punct_lst):
                #    continue

                if(w in self.total_word_lst):
                    stemmedWord = snow_stemmer.stem(w)
                    stem_words.append(stemmedWord)
                    self.addToIndex(stemmedWord,word_pos)
                    word_pos += 1

        else:
            #print("Using Default Stemmer")
            krovetz_stemmer = Stemmer()
            word_pos = 0
            for w in words:
                #if(not w.isalnum()):  #need to change this
                #    continue

                if(w in self.total_word_lst):
                    stemmedWord = krovetz_stemmer.stem(w)
                    stem_words.append(stemmedWord)
                    #self.addToIndex(stemmedWord,word_pos)
                    self.addToIndex(stemmedWord,word_pos)
                    word_pos += 1

        self.document_info[self.docID] = len(stem_words)
        return stem_words




    def delta_decode(self):
        self.decodedIndex = self.index
        for word in self.index:
            for i in range(len(self.index[word])):
                for j in range(2,len(self.index[word][i])):
                    self.decodedIndex[word][i][j] +=  self.index[word][i][j-1] 
        '''
        print()
        for word in self.decodedIndex:
            print("The word is " + word + " and the list is ")
            print(self.decodedIndex[word])
            print()
        '''
        return
        


    def localParser(self):
        periodic_write_counter = 0
        document_count = 0
        num_file_writes = 0

        if(Path("./document_to_id.json").is_file()):
            print("file exists")
            os.remove("./document_to_id.json") 

        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                #print(os.path.join(root, name))
                # Opening JSON file

                self.currFile = name
                self.docID = document_count
                self.document_to_id[name] =  self.docID
                document_count += 1

                f = open(os.path.join(root, name))

                b_raw = json.load(f)
                html = b_raw["content"]
                soup = BeautifulSoup(html, "html.parser")
            
                for data in soup(['style', 'script','a']):
                    data.decompose()
            
                #data by retrieving the tag content
                alltxtcontent = ' '.join(soup.stripped_strings)

                words = word_tokenize(alltxtcontent.lower())
                stem_words = self.Stemming(words)
                print(stem_words)
                return
                #Use to check the stemmer output
                #for e1,e2 in zip(words,stem_words):
                #        print(e1+' ----> '+e2)

                #Use to check the outfile
                #self.displayIndex()
                #self.write_index_to_file()
                #self.read_index_from_file()
                #sys.exit(0)

                #Periodic writing to the file
                periodic_write_counter += 1

                if(periodic_write_counter>1000):
                    num_file_writes += 1
                    print(str(num_file_writes) + ") successfully written to file")
                    #self.compute_tf_idf_score() #uncomment for debugging 
                    self.write_index_to_file()
                    self.write_document_id_to_file()
                    self.write_num_words_to_file()

                    periodic_write_counter = 0
                    #return #uncomment for debugging 

        return

if __name__ == "__main__":

    idx = Indexer()
    idx.localParser()
    idx.write_num_words_to_file()

    #for i in range(5):
    #    print()
    #idx.delta_encode()
    #idx.delta_decode()
    #idx.compute_tf_idf_score()
    #idx.displayIndex()
    #idx.write_index_to_file()