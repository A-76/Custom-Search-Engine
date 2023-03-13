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

        #boolean var to see if all the terms are present or not
        self.final_valid_query = []
        #with open("./id_to_document.json", "r") as outfile:  #change it to id_to_document
        #    x = outfile.read()

        #self.id_to_document = self.decoder.decode(x)
        #
        self.K = 15 #returns the top 10 results
        self.boost_val = 5
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
                        #print("Word is present in the dictionary")
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
        '''
        1) all words present in the query must exist 
        2) if any word does not exist then just return the documents the documents common to the words ignoring position
        '''

        positional_difference = self.final_valid_query[upper_term_idx][1] - self.final_valid_query[lower_term_idx][1]
        best_documents,corresponding_tf_idf = self.__positional_linear_merge__(lower_term_idx,upper_term_idx,positional_difference,best_documents,corresponding_tf_idf)
        return best_documents,corresponding_tf_idf
    
        
    
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
            print(self.final_valid_query)
            while(j<len(self.final_valid_query)):
                best_documents,corresponding_tf_idf = self.positional_search_for_query(i,j,best_documents,corresponding_tf_idf)
                i+=1
                j+=1

            #best_documents1 = self.__linear_merge__()
            
        print("The most relevant documents are - ")
        print(best_documents)
        #print(best_documents1)
        return best_documents
    
    def search(self,query):
        #print(f"Your query is {query.split()}")
        if(query==''):
            return
        
        start_time = time.time()
        query = query.lower()
        self.query = query.split()
        self.find_relevant_word_to_file()
        self.get_postings_for_query()
        best_documents = self.display_top_results()
        duration = time.time() - start_time
        print(f"The time taken for retrieving the posting list is {duration} seconds")
        return best_documents,duration
         

if __name__ == "__main__":
    query = input("Enter your query! \n")
    s = Searcher()
    s.search(query)