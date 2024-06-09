from flask import Flask, request, render_template, jsonify
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import networkx as nx
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import string

app = Flask(__name__)

# Preload NLTK data
nltk.download('punkt')

# Initialize Sastrawi stopword remover
stopword_factory = StopWordRemoverFactory()
stop_words = set(stopword_factory.get_stop_words())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form['text']
    if not text:
        return jsonify({"error": "No text provided."})

    # Get the compression range
    range_value = int(request.form['range'])
    compression_ratio = range_value / 100.0

    # Casefolding (Convert to lowercase)
    text = text.lower()

    # Replace multiple spaces with a single space using regex
    text = re.sub(r'\s+', ' ', text)

    # Tokenize sentences
    sentences = sent_tokenize(text)

    # Tokenize words and remove punctuation
    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
    tokenized_sentences = [[word for word in sentence if word not in string.punctuation] for sentence in tokenized_sentences]

    # Remove stopwords (Bahasa Indonesia)
    preprocessed_sentences = []
    for sentence in tokenized_sentences:
        sentence = [word for word in sentence if word.lower() not in stop_words]
        preprocessed_sentences.append(' '.join(sentence))

    # TF-IDF Weighting
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(preprocessed_sentences)

    # Cosine Similarity
    similarity_matrix = cosine_similarity(vectors)

    # TextRank Algorithm
    graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(graph)
    ranked_sentences = sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)

    # Summary Generation
    num_sentences = max(1, int(len(ranked_sentences) * compression_ratio))
    summary_sentences = ranked_sentences[:num_sentences]
    # Sort summary sentences by their original order
    summary_sentences = sorted(summary_sentences, key=lambda x: x[2])
    summary = '. '.join([sentence for _, sentence, _ in summary_sentences])
    summary = summary.replace('..', '.')  # Replace double dots with a single dot if any

    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
