import requests
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from bs4 import BeautifulSoup
from heapq import nlargest


# Set up the API endpoint and parameters
url = 'https://newsapi.org/v2/everything'
api_key = 'API_KEY'
query = 'adani'

# Set up the request headers and parameters
headers = {'Authorization': f'Bearer {api_key}'}
params = {'q': query, 'pageSize': 10, 'domains': 'ndtv.com'}

# Send the request and get the response
response = requests.get(url, headers=headers, params=params)
data = response.json()

# Extract the article URLs
articles = data['articles']
urls = [article['url'] for article in articles]

def titl(u):
    url = u
    r = requests.get(url)
    htmlContent = r.content
    # print(htmlContent)

    soup = BeautifulSoup(htmlContent, 'html.parser')

    title = soup.find('h1', {"class": "sp-ttl"})
    print(title.string)
    print()


# base = {"NDTV": "https://www.ndtv.com", "S": "aa"}
for i in range(0,5):
    print(i+1, end ="")
    print(".TITLE :", end="")
    titl(urls[i])




desc = soup.find('h2', {"class" : "sp-descp"})
print("HEADLINE" + desc.string)
print()


ps = soup.find_all('p')
text = ""
for i in range(len(ps)):
    if ps[i] is not None and ps[i].string is not None:
        text += " " + ps[i].string
    # print(ps[i].string)

# summarizer part
stopwords = list(STOP_WORDS)
nlp = spacy.load('en_core_web_sm')


# print(text)
docs=nlp(text)
tokens=[token.text for token in docs]

# checking word frequency
punctuation=punctuation+'\n'
word_frequecy={}
for word in docs:
    if word.text.lower() not in stopwords:
        if word.text.lower() not in punctuation:
            if word.text not in word_frequecy.keys():
                word_frequecy[word.text]=1
            else:
                word_frequecy[word.text]+=1
#check max frequency
max_frequency=max(word_frequecy.values())

# gettingfrequency divided by max frequency
for word in word_frequecy.keys():
    word_frequecy[word]=word_frequecy[word]/max_frequency

# tokens of sentence are made
sentence_tokens=[sent for sent in docs.sents]

# score of sentence is calculated
sentence_score={}
for sent in sentence_tokens:
    for word in sent:
        if word.text.lower() in word_frequecy.keys():
            if len(sent.text.split(' '))<30:
                if sent not in sentence_score.keys():
                    sentence_score[sent]=word_frequecy[word.text.lower()]
                else:
                    sentence_score[sent]+=word_frequecy[word.text.lower()]

# percentage of summary is made
select_length = int(len(sentence_tokens)*0.3)

summary=nlargest(select_length, sentence_score, key=sentence_score.get)

# final part the summary is joined
final_summary=[word.text for word in summary]
summary=' '.join(final_summary)


print(summary)
