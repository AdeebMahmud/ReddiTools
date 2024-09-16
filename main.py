
import nltk
import urllib.request
import bs4 as bs
import string
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from gensim.models import Word2Vec
nltk.download('punkt')
nltk.download('stopwords')

# send the url request to open and read the website
# read the article with beautiful soup lxml parser
scrapped_data = urllib.request.urlopen(
    'https://en.wikipedia.org/wiki/Machine_learning')
article = scrapped_data.read()
# parse only the paragraph tag inside the website HTML
parsed_article = bs.BeautifulSoup(article, 'lxml')
paragraphs = parsed_article.find_all('p')
# get the string of the website from the paragraph tag
article_text = ""
for p in paragraphs:
    article_text += p.text

processed_article = article_text.lower()
processed_article = re.sub(r'\s+', ' ', processed_article)
processed_article = re.sub(
    r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]', '', processed_article)
all_sentences = sent_tokenize(processed_article)
all_words = [word_tokenize(sent) for sent in all_sentences]

# Removing Stop Words
stops = set(stopwords.words('english'))
for i in range(len(all_words)):
    all_words[i] = [w for w in all_words[i] if w not in stops]

#word2vec = Word2Vec(all_words, min_count=2)
#vocabulary = word2vec.wv.vocab
