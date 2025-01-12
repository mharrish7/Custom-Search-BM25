from collections import defaultdict
from math import log
import string
import sqlite3
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
import requests
nltk.download('stopwords')
import re


index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
documents: dict[str, str] = {}
titles: dict[str, str] = {}

def normalize_string(content: str) -> str:
    # 1. Lowercasing
  content = content.lower()

  # 2. Punctuation Removal
  content = re.sub(r"[^\w\s]", "", content)

  # 3. Stop Word Removal
  stop_words = set(stopwords.words('english'))
  words = content.split()
  filtered_words = [word for word in words if word not in stop_words]

  # 4. Stemming
  stemmer = PorterStemmer()
  stemmed_words = [stemmer.stem(word) for word in filtered_words]

  normalized_content = " ".join(stemmed_words)
  return normalized_content















def index_urls(data):
    for url, content in data:
        documents[url] = content
        words = normalize_string(content).split(" ")
        for word in words:
            index[word][url] += 1












conn = sqlite3.connect('crawled_urls.db') 
c = conn.cursor()
c.execute("SELECT url, content FROM url_data")
data = c.fetchall()
index_urls(data)
c.execute("SELECT url, title from url_data")
data = c.fetchall()
for url, title in data:
    titles[url] = title










average_length = sum(len(d) for d in documents.values()) / len(documents)














def idf(keyword: str):
    N = len(documents)
    n_kw = len(index[keyword])
    return log((N - n_kw + 0.5) / (n_kw + 0.5) + 1)
















def bm25(keyword) -> dict[str, float]:
    result = {}
    keyword = normalize_string(keyword)
    idf_score = idf(keyword)
    k1 = 1.5
    b = 0.75
    for url, freq in index[keyword].items():
        numerator = freq * (k1 + 1)
        denominator = freq + k1 * (1 - b + b * len(documents[url]) / average_length)
        result[url] = idf_score * numerator / denominator
    return result












def update_url_scores(old: dict[str, float], new: dict[str, float]):
    for url, score in new.items():
        if url in old:
            old[url] += score
        else:
            old[url] = score
    return old




















def search(query: str) -> dict[str, float]:
    keywords = normalize_string(query).split(" ")
    url_scores: dict[str, float] = {}
    for kw in keywords:
        kw_urls_score = bm25(kw)
        url_scores = update_url_scores(url_scores, kw_urls_score)
    result = []
    for url, score in url_scores.items():
        result.append([score,url])
    result.sort(reverse=True)
    return result




















def main_query(query):
    results = search(query)
    result_urls = [[url,titles.get(url, "No Title Found")] for score,url in results]
    return result_urls