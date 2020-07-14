import pandas as pd 
import re
import nltk
#nltk.download("stopwords") 			# uncomment if FIRST TIME RUNNING
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
import tensorflow as tf
import tensorflow_hub as hub
from keras.models import Sequential
from keras import layers

filename = "boulder_training.csv"
styles = ["dyno", "crack", "traverse", "steep", "technical", "mantle", "face"]
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
    text = " ".join(word for word in text.split() if word not in STOPWORDS)

    return text

def naive_bayes(x_train, x_test, y_train, y_test):
	from sklearn.naive_bayes import MultinomialNB

	nb = Pipeline([("vect", CountVectorizer()),
	               ("tfidf", TfidfTransformer()),
	               ("clf", MultinomialNB()),
	              ])
	nb.fit(x_train, y_train)
	y_pred = nb.predict(x_test)

	print("NB Accuracy %s" % accuracy_score(y_pred, y_test))
	print(classification_report(y_test, y_pred, target_names=styles))

def linear_svm(x_train, x_test, y_train, y_test):
	from sklearn.linear_model import SGDClassifier

	sgd = Pipeline([("vect", CountVectorizer()),
	                ("tfidf", TfidfTransformer()),
	                ("clf", SGDClassifier(alpha=.00175, max_iter=15, random_state=5)), # hinge loss, l2 reg
	               ])
	sgd.fit(x_train, y_train)
	y_pred = sgd.predict(x_test)

	print("SVM Accuracy %s" % accuracy_score(y_pred, y_test))
	print(classification_report(y_test, y_pred, target_names=styles))

def log_reg(x_train, x_test, y_train, y_test):
	from sklearn.linear_model import LogisticRegression

	logreg = Pipeline([("vect", CountVectorizer()),
	                ("tfidf", TfidfTransformer()),
	                ("clf", LogisticRegression(n_jobs=1, C=90000, max_iter=80)),
	               ])
	logreg.fit(x_train, y_train)
	y_pred = logreg.predict(x_test)

	print("LogReg Accuracy %s" % accuracy_score(y_pred, y_test))
	print(classification_report(y_test, y_pred, target_names=styles))

def neural_net(x_train, x_test, y_train, y_test):
	# todo: add pretrained model
	pretrained = "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1"		# words not in vocabulary
	hub_layer = hub.KerasLayer(pretrained, output_shape=[20], input_shape=[], 
                           dtype=tf.string, trainable=True)
	hub_layer(x_train[:3])

	#model = Sequential([
	#		layers.Dense(32, activation="relu", input_shape=[]),		# tune hyperparameter
	#		layers.Dense(7)		# 7 classes
	#	])
	model = Sequential()
	model.add(hub_layer)
	model.add(layers.Dense(32, activation='relu'))
	model.add(layers.Dense(10))

	model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 	# mutually exclusive
              metrics=['accuracy'])
	model.summary()
	#model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=10, batch_size=10, verbose=1)
	#result = model.evaluate(x_test, y_test, verbose=2)
	#print("Keras Accuracy: \n%s", result)



df = pd.read_csv(filename)
df["description"] = df["description"].apply(clean_text)
df.info()
x = df.description		# i think
y = df.climb_style
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=10)

#naive_bayes(x_train, x_test, y_train, y_test)
#linear_svm(x_train, x_test, y_train, y_test)
#log_reg(x_train, x_test, y_train, y_test)
neural_net(x_train, x_test, y_train, y_test)