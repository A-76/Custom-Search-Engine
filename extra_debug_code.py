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