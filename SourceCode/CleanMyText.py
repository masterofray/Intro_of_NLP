'''
Created on   : DS Team June 27, 2023
@author      : Masterofray
Compiler     : Python 3.8

Version 0.01.27
'''


import pandas as pd
import re
import string
from tqdm import tqdm
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class DataCleaning:
  # Initialization
  factory     = StemmerFactory()
  stemmer     = factory.create_stemmer()
  kamus_alay1 = pd.read_csv('https://raw.githubusercontent.com/fendiirfan/Kamus-Alay/main/Kamu-Alay.csv')
  kamus_alay1 = kamus_alay1.set_index('kataAlay')
  kamus_alay2 = pd.read_csv('https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv')
  kamus_alay2 = kamus_alay2.filter(['slang', 'formal'], axis=1)
  kamus_alay2 = kamus_alay2.drop_duplicates(subset=['slang'], keep='first')
  kamus_alay2 = kamus_alay2.set_index('slang')
  stopword1   = list(pd.read_csv('https://raw.githubusercontent.com/datascienceid/stopwords-bahasa-indonesia/master/stopwords_id_satya.txt', header = None)[0])
  custom_word = [] #Isikan dengan 

  @classmethod
  def CleanDataFrame(cls, df, col_name, jum_minimum=None, minimum_kata=0):
    '''
    CleanDataFram(DataFrame, NamaKolom, JumlahDataMinimum, MinimumKata) -> DataFrame
    Hasil dari eksekusi ini mengembalikan dataframe yang berisi data yang telah dibersihkan sesuai DataCleaning.__cleanSentence()__ 
    '''

    final_list_clean = []
    final_list_kotor = []

    if jum_minimum == None: jum_minimum = len(df)
    if len(df) < jum_minimum: raise "Jumlah Data Yang Diinginkan melebihi Data yang Ada"
    i = 0
    current = 0
    
    while i < len(df):
      current_kalimat = df.loc[i][col_name]
      clean_kalimat = cls.__cleanSentence__(current_kalimat)
      if (len(clean_kalimat.split(' ')) > minimum_kata):
        final_list_clean.append(clean_kalimat)
        final_list_kotor.append(current_kalimat)
        current += 1
        if current % 10 == 0:
          print("Memproses {} data".format(current))

      if current == jum_minimum:
        break
      i += 1
    
    data = {
        'raw': final_list_kotor,
        'processed': final_list_clean
    }

    return pd.DataFrame(data)

  @classmethod
  def CleanSentence(cls, text):
    return cls.__cleanSentence__(text)

  @classmethod
  def __cleanSentence__(cls, text):
    '''
    Melakukan prapemrosesan pada suatu kalimat dengan menghilangkan formatting pada kalimat,
    menghilangkan stopword pada kalimat, mengganti kata alay yang sudah terdefinisikan, serta
    melakukan stemming kalimat tersebut.
    '''

    # #
    # Cleaning Formatted Text using Regex
    # #
    text = re.sub(r'http\S+', '', text)
    text = re.sub('(@\w+|#\w+)','',text)
    #will replace the html characters with " "
    text=re.sub('<.*?>', '', text)  
    #To remove the punctuations

    ## kuganti jadi gini biar pasti, kalau pakai cara yang dulu, banyak kata2 yang kegabung -kaenova
    temp_text = list(text)
    for i in range(len(temp_text)):
      if temp_text[i] in string.punctuation:
        temp_text[i] = " "
    text = ''.join(temp_text)
    ## sebelumnya kaya gini -kaenova
    # text = text.translate(str.maketrans(' ',' ',string.punctuation))

    #will consider only alphabets
    text = re.sub('[^a-zA-Z]',' ',text) 
    #will replace newline with space
    text = re.sub("\n"," ",text)
    #will convert to lower case
    text = text.lower()
    # will replace a word
    text = re.sub("(username|user|url|rt|xf|fx|xe|xa)\s|\s(user|url|rt|xf|fx|xe|xa)","",text)
    # will repalce repated char
    text = re.sub(r'(\w)(\1{2,})', r"\1", text)
    # will replace single word
    text = re.sub(r"\b[a-zA-Z]\b","",text)
    # will replace space more than one
    text = re.sub('(s{2,})',' ',text)
    # will join the words
    text=' '.join(text.split())

    text_split = text.split(' ')
    # #
    # Mengganti kata-kata yang tidak baku
    # aku gapakai try catch lagi, lebih simple malah ini
    # #
    for i in range(len(text_split)):
      if text_split[i] in cls.kamus_alay1.index:
        text_split[i] = cls.kamus_alay1.loc[text_split[i]]['kataBaik']
      elif text_split[i] in cls.kamus_alay2.index:
        text_split[i] = cls.kamus_alay2.loc[text_split[i]]['formal']
      else:
        pass

    # #
    # Stemming
    # #
    stemmed_text = cls.stemmer.stem(text)

    # #
    # Removing Stopwords and custom word
    # #
    temp_text_split = []
    for i in range(len(text_split)):
      if (text_split[i] not in cls.stopword1) and (text_split[i] not in cls.custom_word):
        temp_text_split.append(text_split[i])

    final_text = ' '.join(temp_text_split)
    
    return final_text

if __name__ == '__main__':
    data        = pd.read_csv('./raw_text.csv')
    data_clean  = DataCleaning.CleanDataFrame(df           = data, 
                                              col_name     = 'raw', 
                                              jum_minimum  = 500, 
                                              kata_minimum = 10,
                                             )
    data_clean