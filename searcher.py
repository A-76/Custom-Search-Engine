import msgspec
import numpy as np
import os
import json
import sys
import time

class Searcher():
    def __init__(self):
        self.decoder = msgspec.json.Decoder()
        #Below are all different variations of representing the query to optimize file access
        self.query = []
        self.term_to_file = {}
        self.file_to_terms = {} #This dictionary will specify all the words present in a given file for ease of access.
        self.posting_lists = {}

        #with open("./document_to_id.json", "r") as outfile:  #change it to id_to_document
        #    x = outfile.read()

        #self.id_to_document = self.decoder.decode(x)
        #
        self.K = 10 #returns the top 10 results
        return
    
    def get_postings_for_query(self):
        #This function returns the posting list for a given word
        #if the word does not exist then it returns an empty list
        basepath = "./IndexStructure/"
        for character in self.file_to_terms:
            for file_number in self.file_to_terms[character]:
                posting_list_location = basepath + character + "/" + str(file_number) + ".json"
                with open(posting_list_location, "r") as outfile:
                        x = outfile.read()

                words_list = self.decoder.decode(x)
                for term in self.file_to_terms[character][file_number]:
                    #print(f"The posting list for the term {term} is - ")
                    #print(words_list[term])
                    self.posting_lists[term] = words_list[term].copy()
                    pass
        return
    
    def __character_to_query__(self,query):
        character_to_query = {}
        for term in query:
            if(term[0] in character_to_query.keys()):
                character_to_query[term[0]].append(term)
            else:
                character_to_query[term[0]] = [term] 
             
        return character_to_query

    def find_relevant_word_to_file(self):
        #Where query is a  list of query terms.
        query = self.query
        basepath = "./IndexStructure/"
        character_to_query =  self.__character_to_query__(query)

        for character in character_to_query:
            word_to_file_location = basepath + character + "/word_to_file.json"
            with open(word_to_file_location, "r") as outfile:
                        x = outfile.read()
            word_to_file = self.decoder.decode(x)
            self.file_to_terms[character] = {}

            for term in character_to_query[character]:
                    if(term in word_to_file.keys()):
                        print("Word is present in the dictionary")
                        file_number = word_to_file[term]
                        self.term_to_file[term] = file_number
                        if(file_number in self.file_to_terms[character].keys()):
                            self.file_to_terms[character][file_number].append(term)
                        else:
                            self.file_to_terms[character][file_number] = [term]
                    else:
                        print(f'The word "{term}" is not present in the dictionary.')
                        
        return
    
    def __high_score__(self,best_documents,corresponding_tf_idf,document):
        if(type(document[-1])==list):
            document.append(0)
        best_documents.append(document[0])
        corresponding_tf_idf.append(document[-1])
        #print(document)
        for i in range (self.K,0,-1):
            #print(document)
            #print(corresponding_tf_idf[i])
            #print(corresponding_tf_idf[i-1])
            #print()
            #there is some issue here, for some instances there is no tf-idf being computed
            
            if(corresponding_tf_idf[i] > corresponding_tf_idf[i-1]):
                #need to swap the value
                new_doc = best_documents[i]
                new_tf_idf = corresponding_tf_idf[i]

                best_documents[i] = best_documents[i-1]
                corresponding_tf_idf[i] = corresponding_tf_idf[i-1]

                best_documents[i-1] = new_doc
                corresponding_tf_idf[i-1] = new_tf_idf
            
            else:
                break
                 
        return best_documents[:-1],corresponding_tf_idf[:-1] #discarding the K + 1 entry
    

    def __linear_merge__(self):
        return
    
    def display_top_results(self):
        best_documents = [0 for i in range(self.K)]
        corresponding_tf_idf = [0 for i in range(self.K)]
        ctr = 0
        if(len(self.query)==1):
            #Single term query, only need to display the top rankings based on tf-idf at the moment
            posting_list = self.posting_lists[self.query[0]]
            for document in posting_list:
                #print("The document is ")
                #print(document)
                best_documents,corresponding_tf_idf = self.__high_score__(best_documents,corresponding_tf_idf,document)
                #print("The updated best documents and tf idf values are ")
                #print(best_documents)
                #print(corresponding_tf_idf)
                #print()
                #if(ctr == 15):
                #     return
                #ctr += 1  
        else:
            #Need to perform a linear merge to obtain the best results

            pass
        print("The most relevavnt documents are - ")
        print(best_documents)
        return
    
    def search(self,query):
        #print(f"Your query is {query.split()}")
        if(query==''):
            return
        
        start_time = time.time()
        query = query.lower()
        self.query = query.split()
        self.find_relevant_word_to_file()
        self.get_postings_for_query()
        self.display_top_results()
        duration = time.time() - start_time
        print(f"The time taken for retrieving the posting list is {duration} seconds")
        return
         



if __name__ == "__main__":
    query = input("Enter your query! \n")
    s = Searcher()
    s.search(query)