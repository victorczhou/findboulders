import pandas as pd 
import re
import nltk
from nltk.corpus import stopwords

filename = "boulder_training.csv"
STOPWORDS = set(stopwords.words("english"))

def clean_text(text):
    # remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # remove the characters [\], ['] and ["] and 0x91-0x94
    text = re.sub(r"\\", "", text)    
    text = re.sub(r"\'", " ", text)    			# filters all quotes into spaces -> stopwords remove s
    text = re.sub(r"\"", " ", text)
    text = re.sub(r"", " ", text) 
    text = re.sub(r"", " ", text) 
    text = re.sub(r"", " ", text)
    text = re.sub(r"", " ", text)
    
    # convert text to lowercase
    text = text.strip().lower()
    
    # replace punctuation characters with spaces
    filters='!"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
    translate_dict = dict((c, " ") for c in filters)
    translate_map = str.maketrans(translate_dict)
    text = text.translate(translate_map)

    #remove stopwords
    text = " ".join(word for word in text.split() if word is not in STOPWORDS)

    return text

df = pd.read_csv(filename)
df["description"] = df["description"].apply(clean_text)
