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
from nltk.stem.snowball import SnowballStemmer, PorterStemmer
from krovetzstemmer import Stemmer
import msgspec

import numpy as np
from collections import defaultdict
import hashlib

encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder()

def write_document_id_to_file(id_to_document):                 
        a = encoder.encode(id_to_document)
        with open("./id_to_document2.json", "ab") as outfile:
            outfile.write(a)
        print("written to file successfully")
        return

def read_doc_id__from_file():
        with open("./id_to_document2.json", "r") as outfile:  #change it to id_to_document
            x = outfile.read()

        id_to_document = decoder.decode(x)
        print("Read the file successfully")
        return id_to_document

if __name__ == "__main__":
    path = "./developer/DEV/" #"/home/adithya/Desktop/trial/tempTotalDoc/" #
    id_to_document = {}
    document_count = 0
    periodic_write_counter = 0
    num_file_writes= 0
    for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                # print(os.path.join(root, name))
                # Opening JSON file
                #print(name)

                currFile = name
                docID = document_count
                

                f = open(os.path.join(root, name))

                b_raw = json.load(f)

                id_to_document[docID] =  [name,b_raw["url"]]
                document_count += 1

                periodic_write_counter += 1
                if(periodic_write_counter > 1000):  # why 1000
                    num_file_writes += 1
                    print(str(num_file_writes) + ") successfully written to file")
                    periodic_write_counter = 0
                    #break

    write_document_id_to_file(id_to_document)
    read_doc_id__from_file()