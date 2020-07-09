import pandas as pd 
import re

filename = "boulder_training.csv"

def clean_text(text):
    # remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # remove the characters [\], ['] and ["] and ascii 0x91-0x94
    text = re.sub(r"\\", "", text)    
    text = re.sub(r"\'", "", text)    
    text = re.sub(r"\"", "", text)
    text = re.sub(b"<0x91>", "", text) 
    text = re.sub(b"<0x92>", "", text) 
    text = re.sub(b"<0x93>", "", text)
    text = re.sub(b"<0x94>", "", text)    
    
    # convert text to lowercase
    text = text.strip().lower()
    
    # replace punctuation characters with spaces
    filters='!"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
    translate_dict = dict((c, " ") for c in filters)
    translate_map = str.maketrans(translate_dict)
    text = text.translate(translate_map)

    return text

df = pd.read_csv(filename)
df["description"] = df["description"].apply(clean_text)

print(df)