import os
import json
from bs4 import BeautifulSoup
import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import words
import shutil
import random

#nltk.download('words')
#nltk.download('punkt')

from pathlib import Path
import nltk
from nltk.stem.snowball import SnowballStemmer,PorterStemmer
from krovetzstemmer import Stemmer
import msgspec

import numpy as np
from collections import defaultdict

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
        self.encoder = msgspec.json.Encoder()
        self.decoder = msgspec.json.Decoder()

        #Hyperparameter Values
        self.num_files_per_letter = 10
        self.write_binary = True

        self.updatedIndex = {}
        self.word_to_file = {}

        return
    
    def updatedAddToIndex(self,word,position):
        #Each token/word needs to have a list of documents that it is present in along with the tf-idf score.
        first_char = word[0]
        if(first_char not in self.updatedIndex.keys()):
            first_char = "extra"


        correct_dictionary = self.updatedIndex[first_char]

        if(word not in correct_dictionary.keys()):
            self.updatedIndex[first_char][word] = []
            new_entry = [self.docID,[position]]
            self.updatedIndex[first_char][word].append(new_entry)

        else:
            #print(self.index[word])
            if(correct_dictionary[word][-1][0]  == self.docID):  #This line is going to check the docID of the previous insertion, if same as currID then add to same list
                    #print("The length of the list is ")
                    #print(self.index[word][-1])
                    val_to_add = position - self.updatedIndex[first_char][word][-1][1][-1]
                    self.updatedIndex[first_char][word][-1][1].append(val_to_add)

            else:                    
                new_entry = [self.docID,[position]]
                self.updatedIndex[first_char][word].append(new_entry)

        return
    
    def generate_all_directories(self):
        path = "./IndexStructure/"

        if(os.path.exists(path)):
            self.destroy_all_directories()

        os.mkdir(path)
        for i in range(97,123):
            os.mkdir(path + chr(i))
            self.updatedIndex[chr(i)] = {}
            self.word_to_file[chr(i)] = {}

        self.updatedIndex["extra"] = {}
        self.word_to_file["extra"] = {}
        
        os.mkdir(path + "extraCharacters")
        return
    
    def destroy_all_directories(self):
        path = "./IndexStructure/"
        shutil.rmtree(path)
        if(os.path.exists("./num_words.txt")):
            os.remove("./num_words.txt")
        
        if(os.path.exists("./document_to_id.json")):
            os.remove("./document_to_id.json")

        if(os.path.exists("./TotalIndex.json")):
            os.remove("./TotalIndex.json")
        return
    
    def updated_write_num_words_to_file(self):
        with open("./num_words.txt", "w") as outfile:
            total_words  = 0
            for key in self.word_to_file.keys():
                total_words += len(self.word_to_file[key].keys())
            outfile.write(str(total_words))
        return
        
    def write_document_id_to_file(self):
        if(not self.write_binary):
            json_object = json.dumps(self.document_to_id, indent = 4) 

            with open("./document_to_id.json", "a+") as outfile:
                outfile.write(json_object)
                 
        else:
            a = self.encoder.encode(self.document_to_id)
            with open("./document_to_id.json", "ab") as outfile:
                outfile.write(a)

        self.document_to_id.clear()
        return

    def create_file_to_word(self,file_number_dict):
        #sorted_dict  = dict(sorted(file_number_dict.items(), key=lambda x:x[1]))
        res =defaultdict(list)
        for key, val in sorted(file_number_dict.items()):
            res[val].append(key)
        #print(res)
        return res
    
    def create_json(self,file_to_word,file_number,char):
        corresponding_json = {}
        for word in file_to_word[file_number]:
            corresponding_json[word] = self.updatedIndex[char][word]
        
        return corresponding_json

    def updated_read_index_from_file(self):
        basepath = "./IndexStructure/"
        disk_index = {}
        for char in self.updatedIndex:
            for file_number in range(1,self.num_files_per_letter+1):
                newpath = basepath + char + "/" + str(file_number) + ".json"

                if(not os.path.exists(newpath)):
                    continue

                if(not self.write_binary):
                    with open(newpath, "r") as readfile:
                        self.index = json.load(readfile)
                else:
                    with open(newpath, "r") as outfile:
                        x = outfile.read()
                    if(char not in disk_index.keys() or (len(disk_index[char].keys())==0)):
                        disk_index[char] = self.decoder.decode(x)

                    else:
                        disk_index[char].update(self.decoder.decode(x))
        #self.displayupdatedIndex()
        return disk_index

    def merge(self):
        #call read index from file here
        disk_index = self.updated_read_index_from_file()
        print(disk_index)
        curr_index = self.updatedIndex

        for char in curr_index:
            if(char not in disk_index.keys()):
                disk_index[char] = {}

            for word in curr_index[char]:
                if(word not in disk_index[char].keys()):
                    #first word occurrence after the write to file.
                    disk_index[char][word] = curr_index[char][word].copy()   

                else:
                    disk_index[char][word] += curr_index[char][word]
        
        self.updatedIndex = disk_index
        return
    
    def updated_write_index_to_file(self):
        self.merge()
        basepath = "./IndexStructure/"
        for char in self.updatedIndex:
            res = self.create_file_to_word(self.word_to_file[char])
            for file_number in res.keys():
                newpath = basepath + char + "/" + str(file_number) + ".json"
                corresponding_json = self.create_json(res,file_number,char)

                if(not self.write_binary):
                    json_object = json.dumps(corresponding_json, indent = 4) 
                    with open(newpath, "w") as outfile:
                        outfile.write(json_object)
                else:
                    a = self.encoder.encode(corresponding_json)
                    with open(newpath, "wb") as outfile:
                        outfile.write(a)
        
        for char in self.updatedIndex:
            self.updatedIndex[char].clear()
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
                tf_idf = float(tf*idf)
                document.append(tf_idf)

        return 

     
    def displayupdatedIndex(self):
        print()
        for char in self.updatedIndex:
            print(f"The character is {char}")
            for word in self.updatedIndex[char]:
                print("The word is " + word + " and the list is ")
                print(self.updatedIndex[char][word])
                print()
        return

    def update_word_to_file(self,word):
        first_char = word[0]
        if(first_char not in self.word_to_file.keys()):
            first_char = "extra"
        if(word not in self.word_to_file[first_char].keys()):
            self.word_to_file[first_char][word] = random.randint(1, self.num_files_per_letter)
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
                    #self.addToIndex(stemmedWord,word_pos)
                    self.updatedAddToIndex(stemmedWord,word_pos)
                    self.update_word_to_file(stemmedWord)
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
                    #self.addToIndex(stemmedWord,word_pos)
                    self.updatedAddToIndex(stemmedWord,word_pos)
                    self.update_word_to_file(stemmedWord)
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
                    #self.addToIndex(stemmedWord,word_pos)
                    self.updatedAddToIndex(stemmedWord,word_pos)
                    self.update_word_to_file(stemmedWord)
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
                #print(stem_words)
                
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

                if(periodic_write_counter>0):
                    num_file_writes += 1
                    print(str(num_file_writes) + ") successfully written to file")
                    #self.compute_tf_idf_score() #uncomment for debugging 
                    self.displayupdatedIndex()

                    #self.write_num_words_to_file()
                    self.updated_write_num_words_to_file()
                    self.write_document_id_to_file()

                    self.updated_write_index_to_file()
                    #print("This is the recovered index")
                    #self.updated_read_index_from_file()
                    if(periodic_write_counter==7):
                        sys.exit()

                    
                    
                    print()
                    print()
                    print()
                    #periodic_write_counter = 0

                    #return #uncomment for debugging 

        return

if __name__ == "__main__":


    idx = Indexer()
    idx.generate_all_directories()
    idx.localParser()
    idx.write_num_words_to_file()

    #for i in range(5):
    #    print()
    #idx.delta_encode()
    #idx.delta_decode()
    #idx.compute_tf_idf_score()
    #idx.displayIndex()
    #idx.write_index_to_file()