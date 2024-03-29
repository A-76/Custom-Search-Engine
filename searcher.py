import msgspec
import numpy as np
from numpy import linalg as LA
import os
import json
import sys
import time
from nltk.tokenize import word_tokenize
from krovetzstemmer import Stemmer

class Searcher():
    def __init__(self,tdm=None,word_to_row=None):
        self.decoder = msgspec.json.Decoder()
        #Below are all different variations of representing the query to optimize file access
        self.query = []
        self.term_to_file = {}
        self.file_to_terms = {} #This dictionary will specify all the words present in a given file for ease of access.
        self.posting_lists = {}

        #boolean var to see if all the terms are present or not
        self.final_valid_query = []
        with open("./id_to_document2.json", "r") as outfile:  #change it to id_to_document
            x = outfile.read()

        self.id_to_document = self.decoder.decode(x)
        #
        self.K = 10 #returns the top 10 results
        self.boost_val = 1

        #The below are values for computing cosine similarity
        self.tdm = tdm 
        self.word_to_row = word_to_row
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
                if(term[0].isalpha()):
                    character_to_query[term[0]].append(term)
                else:
                    character_to_query["extra"].append(term)
            else:  
                if(term[0].isalpha()):
                    character_to_query[term[0]] = [term] 
                else:
                    character_to_query["extra"] = [term] 
             
        return character_to_query

    def find_relevant_word_to_file(self):
        #Where query is a  list of query terms.
        query = self.query
        basepath = "./IndexStructure/"
        character_to_query =  self.__character_to_query__(query)
        #print(character_to_query)
        for character in character_to_query:
            if(character.isalpha()):  #If the word is not an alphabet then directory is "extra"
                word_to_file_location = basepath + character + "/word_to_file.json"
                
            else:
                word_to_file_location = basepath + "extra" + "/word_to_file.json"
            

            with open(word_to_file_location, "r") as outfile:
                        x = outfile.read()
            word_to_file = self.decoder.decode(x)
            self.file_to_terms[character] = {}    

            for term in character_to_query[character]:
                    if(term in word_to_file.keys()):
                        #print("Word is present in the dictionary " + term)
                        file_number = word_to_file[term]
                        self.term_to_file[term] = file_number

                        position_of_term_in_query  = query.index(term)

                        self.final_valid_query.append([term,position_of_term_in_query])
                        if(file_number in self.file_to_terms[character].keys()):
                            self.file_to_terms[character][file_number].append(term)
                        else:
                            self.file_to_terms[character][file_number] = [term]
                    else:
                        self.term_to_file[term] = -1 #the term is not present

                        #print(f'The word "{term}" is not present in the dictionary.')                       
        return
    
    def __high_score__(self,best_documents,corresponding_tf_idf,document,existing_doc_index = -1):
        if(existing_doc_index== -1): 
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
        else:
            for i in range (existing_doc_index,0,-1):
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
                    
            return best_documents,corresponding_tf_idf #discarding the K + 1 entry
    
    def delta_decode(self,lst):
        decoded_lst = lst.copy()
        for i in range(1,len(lst)):
            decoded_lst[i] += decoded_lst[i - 1] 

        return decoded_lst

    def __linear_merge__(self):
        i = 0
        j = 0
        best_documents = [0 for i in range(self.K)]
        corresponding_tf_idf = [0 for i in range(self.K)]

        if((self.query[0] in self.posting_lists.keys()) and (self.query[1] in self.posting_lists.keys())):
            #print("gfs")
            plist_1 = self.posting_lists[self.query[0]]
            plist_2 = self.posting_lists[self.query[1]]
            while(i< len(plist_1) and j < len(plist_2)):
                if(plist_1[i][0] == plist_2[j][0]):
                    #common_documents.append(plist_1[i][0])
                    tfidf1 = plist_1[i][-1]
                    tfidf2 = plist_2[j][-1]
                    if(type(tfidf1) == list):
                        tfidf1 =0
                    if(type(tfidf2)==list):
                        tfidf2 =0

                    #corresponding_tf_idf.append(tfidf1+tfidf2)
                    document = [plist_1[i][0],[0,0,0],tfidf1+tfidf2]
                    best_documents,corresponding_tf_idf = self.__high_score__(best_documents,corresponding_tf_idf,document)
                    i+=1
                    j+=1

                elif(plist_1[i][0] > plist_2[j][0]):
                    j+= 1
                else:
                    i+=1
        
        return best_documents
    

    def __parse_positions__(self,positions_term1,positions_term2,required_positional_diff):
        #We are basically boosting the cumulativev tf-idf score by a value of 10 for a document when the pair of words occur as in the query
        i = 0
        j = 0

        decoded_positions1 = self.delta_decode(positions_term1)
        decoded_positions2 = self.delta_decode(positions_term2)

        increment_factor = 0
        #print(f"The required positional diff is {required_positional_diff}")
        while(i< len(decoded_positions1) and j < len(decoded_positions2)):
            if(decoded_positions2[j] - decoded_positions1[i] == required_positional_diff):
                #the words are next to each other
                #print(f"The positions are {decoded_positions2[j]} and {decoded_positions1[i]}")
                increment_factor += self.boost_val
                i+= 1
                j+= 1
            elif(decoded_positions2[j] - decoded_positions1[i] > required_positional_diff):
                i+=1
            else:
                j+=1

        return increment_factor
    

    def __positional_linear_merge__(self,lower_term_idx,upper_term_idx,positional_difference,best_documents,corresponding_tf_idf):
        #print(positional_difference)
        #print(lower_term_idx)
        #print(upper_term_idx)
        i = 0
        j = 0

        #print(self.query[lower_term_idx])
        #print(self.query[upper_term_idx])
        #print(self.posting_lists.keys())
        if((self.final_valid_query[lower_term_idx][0] in self.posting_lists.keys()) and (self.final_valid_query[upper_term_idx][0] in self.posting_lists.keys())):

            plist_1 = self.posting_lists[self.final_valid_query[lower_term_idx][0]]
            plist_2 = self.posting_lists[self.final_valid_query[upper_term_idx][0]]

            while(i< len(plist_1) and j < len(plist_2)):
                if(plist_1[i][0] == plist_2[j][0]):

                    #perform positional_parsing here - 
                    #print(plist_1)
                    #print(plist_2)
                    try:
                        additional_tf_idf = self.__parse_positions__(plist_1[i][1],plist_2[j][1],positional_difference)
                    except:
                        print(plist_1[i][1])
                        print(plist_2)
                    #print(additional_tf_idf)
                    tfidf1 = plist_1[i][-1]
                    tfidf2 = plist_2[j][-1]

                    if(type(tfidf1) == list):
                        tfidf1 =0
                    if(type(tfidf2)==list):
                        tfidf2 =0

                    #corresponding_tf_idf.append(tfidf1+tfidf2)
                    if(plist_1[i][0] in best_documents):
                        #this can happen in queries with more than 2 words. 
                        #print(f"The document appeared twice {plist_1[i][0]}")
                        curr_rank = best_documents.index(plist_1[i][0])
                        #print(f"The old tf idf of the doc is {corresponding_tf_idf[curr_rank]}")
                        #document = [plist_1[i][0],[0,0,0],corresponding_tf_idf[curr_rank] + additional_tf_idf] #we will insert document number again but its fine.
                        #we only need to resort the portion of the list that is ranked higher than the existing document.
                        corresponding_tf_idf[curr_rank] +=  additional_tf_idf
                        #print(f"The new tf idf of the doc is {corresponding_tf_idf[curr_rank]}")
                        #print("The old documents list and the corresponding tf-idf is ")
                        #print(best_documents)
                        #print(corresponding_tf_idf)
                        #print()
                        best_documents,corresponding_tf_idf = self.__high_score__(best_documents,corresponding_tf_idf,[],curr_rank)
                        
                        #print("The new documents list and the corresponding tf-idf is ")
                        #print(best_documents)
                        #print(corresponding_tf_idf)
                        #print()
                    else:
                        document = [plist_1[i][0],[0,0,0],tfidf1+tfidf2+additional_tf_idf]
                        #for queries with exactly 2 words
                        best_documents,corresponding_tf_idf = self.__high_score__(best_documents,corresponding_tf_idf,document)
                    i+=1
                    j+=1

                elif(plist_1[i][0] > plist_2[j][0]):
                    j+= 1
                else:
                    i+=1
        
        return best_documents,corresponding_tf_idf
    
    
    def positional_search_for_query(self,lower_term_idx,upper_term_idx,best_documents,corresponding_tf_idf):


        positional_difference = self.final_valid_query[upper_term_idx][1] - self.final_valid_query[lower_term_idx][1]
        best_documents,corresponding_tf_idf = self.__positional_linear_merge__(lower_term_idx,upper_term_idx,positional_difference,best_documents,corresponding_tf_idf)
        return best_documents,corresponding_tf_idf
    
        
    def rank_by_cosine_similarity(self,best_documents):
        #first need to generate the query vector
        #basically generate a new document with 1's at the location of the word
        best_documents1 = [0 for i in range(self.K)]
        corresponding_cosine_sim = [-1 for i in range(self.K)]
        
        query_vector = np.zeros((self.tdm.shape[0],))
        for term in self.final_valid_query:
            query_vector[self.word_to_row[term[0]]] += 1
        query_vector_norm = LA.norm(query_vector)
        
        for docID in best_documents:
            if(docID>=self.tdm.shape[1]):
                docID1 =self.tdm.shape[1]-1
            document_vector = self.tdm[:,docID1]
            cos_sim = np.dot(query_vector, document_vector)/(query_vector_norm*LA.norm(document_vector))
            document = [docID,[0],cos_sim]
            best_documents1,corresponding_cosine_sim = self.__high_score__(best_documents1,corresponding_cosine_sim,document)
        
        #print(f"The cosine similarity is {cos_sim}")
        return best_documents1
    

    def display_top_results(self): 
        best_documents1 = []
        if(len(self.final_valid_query)==1):
            best_documents = [0 for i in range(self.K)]
            corresponding_tf_idf = [0 for i in range(self.K)]
            ctr = 0
            #Single term query, only need to display the top rankings based on tf-idf at the moment
            posting_list = self.posting_lists[self.final_valid_query[0][0]]
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
            i = 0
            j = 1
            best_documents = [0 for i in range(self.K)]
            corresponding_tf_idf = [0 for i in range(self.K)]
            #print(self.final_valid_query)
            while(j<len(self.final_valid_query)):
                best_documents,corresponding_tf_idf = self.positional_search_for_query(i,j,best_documents,corresponding_tf_idf)
                i+=1
                j+=1

            #best_documents1 = self.__linear_merge__()
            
        #place a try catch here to prevent BT
        #try:
        #    best_documents1 = self.rank_by_cosine_similarity(best_documents)
        #    best_documents = best_documents1
        #except Exception as e:
        #    print("Calculating the cosine similarity failed")

        print("The most relevant documents are - ")
        print(best_documents)
        #print(best_documents1)
        return best_documents
    
    def map_id_to_document(self,best_documents):
        results = []
        #print(self.id_to_document.keys())
        for docID in best_documents:
            try:
                #print(self.id_to_document[str(docID)][1])
                results.append(self.id_to_document[str(docID)][1])
            except Exception as e:
                #results.append(self.id_to_document[str(0)][1])
                #print(docID)
                print(e)
                #print("hi")
        return results
    

    def tokenize_query(self,query):
        stem_words = []
        words = word_tokenize(query.lower())

        krovetz_stemmer = Stemmer()
        for w in words:
            if(not w.isalnum()):  #need to change this
                continue

            if(len(w) == 1 and ((w != 'a') and (w != 'i')) and not w.isnumeric()): #this disregards numbers need to change that.
                continue
            #if(w in self.total_word_lst):
            stemmedWord = krovetz_stemmer.stem(w)
            stem_words.append(stemmedWord)

        return stem_words

    def search(self,query):
        #print(f"Your query is {query.split()}")
        if(query==''):
            return
        
        start_time = time.time()
        #query = query.lower()
        self.query = self.tokenize_query(query)
        self.find_relevant_word_to_file()
        self.get_postings_for_query()
        best_documents = self.display_top_results()
        duration = time.time() - start_time
        best_documents_text = self.map_id_to_document(best_documents)
        #print(best_documents_text)
        print(f"The time taken for retrieving the posting list is {duration} seconds")
        return best_documents_text,best_documents,duration            #best_documents,duration
         

if __name__ == "__main__":
    query = input("Enter your query! \n")
    s = Searcher()
    s.search(query)