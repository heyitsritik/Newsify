import logging
import os

import requests
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from bs4 import BeautifulSoup


from heapq import nlargest
from telegram.ext import *


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

query = ""
# Load Spacy model and stopwords
nlp = spacy.load('en_core_web_sm')
stopwords = list(STOP_WORDS)
punctuation = punctuation + '\n'


# Define command handlers
def start(update, context):
    global query
    query = ''
    """Send a message when the command /start is issued."""
    update.message.reply_text("""
    Welcome to the News Summarizer Bot! This bot will provide you with summaries of the latest news articles based on your choice of topic. Please choose a topic by entering one of the following commands:
    
    -> /current_affairs
    -> /business_and_finance
    -> /politics
    -> /science_and_technology
    -> /entertainment
    -> /sports
    -> For query type /query<space>'your query'
    """)


def current_affairs(update, context):
    """Get current affairs news."""
    global query
    query = 'current affairs'
    procedure(update,query)


def business_and_finance(update, context):
    """Get business and finance news."""
    global query
    query = 'business and finance'
    procedure(update,query)


def politics(update, context):
    """Get politics news."""
    global query
    query = 'politics'
    procedure(update,query)


def science_and_technology(update, context):
    """Get science and technology news."""
    global query
    query = 'science and technology'
    procedure(update,query)


def entertainment(update, context):
    """Get entertainment news."""
    global query
    query = 'bollywood and hollywood'
    procedure(update,query)


def sports(update, context):
    """Get sports news."""
    global query
    query = 'cricket and football'
    procedure(update,query)

def query(update, context):
    """Get your news."""
    global query
    query = context.args[0]
    procedure(update,query)

# def text_handler(update, context):
#     text = update.message.text
#     context.bot.send_message(chat_id=update.effective_chat.id, text=f"You said: {text}")
#     global query
#     query = text
#     procedure(update, query)


def procedure(update,query):
    urls = get_article(query)
    s = len(urls)
    title = ""
    if s < 5 :
        for i in range(0,s):
            title = get_title(urls[i])
            update.message.reply_text(f"{i + 1}. {title}")
    else:
        for i in range(0, 5):
            title = get_title(urls[i])
            update.message.reply_text(f"{i + 1}. {title}")
    update.message.reply_text("Enter your News number: ")
    # pass


def get_title(url):
    r = requests.get(url)
    htmlContent = r.content
    soup = BeautifulSoup(htmlContent, 'html.parser')
    title = soup.find('h1', {"class": "sp-ttl"})
    if title is not None:
        return title.string.strip()
    else:
        return None


def get_article(query):
    api_key = 'YOUR API KEY'
    url = 'https://newsapi.org/v2/everything'

    # Set up the request headers and parameters
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'q': query, 'pageSize': 10, 'domains': 'ndtv.com'}

    # Send the request and get the response
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Extract the article URLs
    articles = data['articles']
    urls = [article['url'] for article in articles if 'ndtv.com' in article['url']]
    # print(urls)
    return urls


def extract_article_info(url):
    r = requests.get(url)
    htmlContent = r.content
    soup = BeautifulSoup(htmlContent, 'html.parser')

    article_info = {}

    # Extract the article title
    title = soup.find('h1', {"class": "sp-ttl"})
    if title is not None:
        article_info['title'] = title.string.strip()


    # Extract the article author and publication date
    author = soup.find('div', {"class": "author"})
    pub_date = soup.find('div', {"class": "upd_dte"})
    if author is not None:
        article_info['author'] = author.text.strip()
    if pub_date is not None:
        article_info['pub_date'] = pub_date.text.strip()

    # Extract the article text
    article_text = []
    paragraphs = soup.find_all('div', {"class": "sp-cn"})
    for paragraph in paragraphs:
        text = paragraph.text.strip()
        if len(text) > 0:
            article_text.append(text)

    # Join the article text into a single string
    article_info['text'] = '\n'.join(article_text)

    return article_info


def summarize_article(update, context):
    """Summarize the article selected by the user."""
    # if query == '':
    #     query = update.message.text
    news_num = int(update.message.text)
    # query = update.message.text
    urls = get_article(query)
    url = urls[news_num-1]
    article_info = extract_article_info(url)

    # Create a Spacy doc object for the article text
    doc = nlp(article_info['text'])

    # Filter out stop words and punctuation marks
    words = [token.text for token in doc if not token.is_stop and not token.text in punctuation]

    # sidd code
    sentence_tokens = [sent for sent in doc.sents]

    # Calculate word frequency and assign scores to sentences
    word_freq = {}
    for word in words:
        if word not in word_freq.keys():
            word_freq[word] = 1
        else:
            word_freq[word] += 1

    max_freq = max(word_freq.values())

    for word in word_freq.keys():
        word_freq[word] = (word_freq[word] / max_freq)

    sentence_scores = {}
    sentences = [sent for sent in doc.sents]
    for sent in sentences:
        for word in sent:
            if word.text in word_freq.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_freq[word.text]
                else:
                    sentence_scores[sent] += word_freq[word.text]


   
    # Get the summary sentences with highest scores
    select_length = int(len(sentence_tokens) * 0.25)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

   
    # final part the summary is joined
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
  

    # Send the summary to the user
    update.message.reply_text(f"Title: {article_info['title']}")
    # update.message.reply_text(f"Author: {article_info['author']}")
    # update.message.reply_text(f"Publication Date: {article_info['pub_date']}")
    update.message.reply_text("Summary: ")
    update.message.reply_text(summary)
    update.message.reply_text(f"Url: {urls[news_num - 1]}")
    update.message.reply_text("click -> /start to reload the menu")


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    """Start the bot."""
    
    # print(bot.get_me())
    updater = Updater('YOUR TELEGRAM API KEY', use_context=True)
    dispatcher = updater.dispatcher

    # Define the command and message handlers,
    start_handler = CommandHandler('start', start)
    current_affairs_handler = CommandHandler('current_affairs', current_affairs)
    business_and_finance_handler = CommandHandler('business_and_finance', business_and_finance)
    politics_handler = CommandHandler('politics', politics)
    science_and_technology_handler = CommandHandler('science_and_technology', science_and_technology)
    entertainment_handler = CommandHandler('entertainment', entertainment)
    sports_handler = CommandHandler('sports', sports)
    query_handler = CommandHandler('query', query)
    summary_handler = MessageHandler(Filters.regex(r'^\d+$'), summarize_article)
    echo_handler = MessageHandler(Filters.text & ~Filters.command, echo)

    # Add the handlers to the dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(current_affairs_handler)
    dispatcher.add_handler(business_and_finance_handler)
    dispatcher.add_handler(politics_handler)
    dispatcher.add_handler(science_and_technology_handler)
    dispatcher.add_handler(entertainment_handler)
    dispatcher.add_handler(sports_handler)
    dispatcher.add_handler(query_handler)
    dispatcher.add_handler(summary_handler)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
