import os
import nltk

nltk_data_dir = "./resources/nltk_data_dir/"
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.clear()
nltk.data.path.append(nltk_data_dir)
nltk.download("vader_lexicon", download_dir=nltk_data_dir)
nltk.download("punkt", download_dir=nltk_data_dir)

import requests
import nltk
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer

keywords = [
    'credit card', 'credit score', 'credit limit', 'annual fee', 'apr',
    'balance transfer', 'rewards', 'cashback', 'points', 'miles',
    'sign-up bonus', 'personal loan', 'student loan', 'mortgage', 'auto loan',
    'debt consolidation', 'interest rate', 'fixed rate', 'variable rate',
    'repayment term', 'collateral', 'savings account', 'checkings account',
    'high-yields savings', 'cd', 'money market account', 'overdraft protection',
    'stocks', 'bonds', 'etf', 'mutual fund', 'ira', '401k', 'robo-advisor',
    'budget', 'debt', 'refinance', 'credit report', 'net worth',
    'financial planning', 'emergency fund', 'income', 'expenses', 'fees',
    'mobile banking', 'digital wallet', 'cryptocurrency', 'peer-to-peer',
    'blockchain', 'online lending', 'credit history', 'credit utilization',
    'credit inquiry', 'credit counseling', 'credit repair', 'home equity loan',
    'payday loan', 'loan term', 'loan application', 'loan approval', 'loan officer',
    'joint account', 'business account', 'account balance', 'bank statement',
    'account fees', 'mobile deposit', 'bank branch', 'bank teller', 'online banking',
    'stock market', 'bond yield', 'investment portfolio', 'dividends', 'capital gains',
    'index fund', 'hedge fund', 'fund manager', 'retirement savings', 'pension plan',
    'retirement account', 'Roth IRA', 'expense tracking', 'budget plan', 'savings goal',
    'monthly budget', 'debt repayment', 'debt relief', 'debt strategy', 'life insurance',
    'health insurance', 'auto insurance', 'home insurance', 'insurance policy', 'premium',
    'deductible', 'coverage', 'claim', 'tax return', 'tax refund', 'tax bracket',
    'tax deduction', 'tax credit', 'financial advisor', 'estate planning', 'will',
    'trust', 'inheritance', 'mobile payment', 'digital banking', 'fintech',
    'blockchain technology', 'cryptocurrency wallet', 'peer-to-peer lending',
    'crowdfunding', 'real estate investment', 'net income', 'gross income',
    'liquidity', 'solvency', 'financial ratio', 'asset', 'liability', 'equity',
    'cash flow', 'interest', 'principal', 'amortization', 'leverage', 'fraud protection',
    'identity theft', 'cybersecurity', 'secure transaction', 'certificate of deposit',
    'money market fund', 'exchange-traded fund', 'inflation', 'deflation', 'recession',
    'economic growth'
]

def extract_relevant_phrases(post_text):
    sentences = nltk.sent_tokenize(post_text)
    
    # POS tagging and chunking
    grammar = r"""
    NP: {<DT|JJ|NN.*>+}                # noun phrases
    VP: {<VB.*><NP|PP|CLAUSE>+$}       # verb phrases
    PP: {<IN><NP>}                     # propositional phrases
    CLAUSE: {<NP><VP>}                 # clauses
    """
    chunk_parser = nltk.RegexpParser(grammar)
    
    relevant_phrases = []
    keyword_set = set(word.lower() for phrase in keywords for word in phrase.split())

    # parse sentences
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)
        tree = chunk_parser.parse(pos_tags)
        
        # parse phrases
        for subtree in tree.subtrees():
            if subtree.label() in {'NP', 'VP', 'PP', 'CLAUSE'}:
                phrase = " ".join(word for word, tag in subtree.leaves())

                # check that we have at least one relevant keyword
                phrase_words = set(word.lower() for word in phrase.split())
                if phrase_words & keyword_set:
                    relevant_phrases.append(phrase)
    
    return relevant_phrases

def top_three_phrases(url):
    r = requests.get(url)
    html = r.text

    soup = BeautifulSoup(html, "html.parser")

    # obtain list of posts from html
    post_list = soup.find_all("div", class_="post")
    post_list.pop()  # to remove bot reply

    # append all posts to a string
    entire_forum = ""
    for text in post_list:
        entire_forum += text.get_text(" ", strip = True)

    # Create an instance of the Vader sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Extract relevant phrases
    relevant_phrases = extract_relevant_phrases(entire_forum)
    ranked_phrases = {}

    for phrases in relevant_phrases:
        if len(phrases.split(' ')) > 1 and len(phrases.split(' ')) < 6:
            scores = analyzer.polarity_scores(phrases)
            ranked_phrases[phrases] = abs(scores['compound'])

    ranked_phrases = sorted(ranked_phrases.items(), key=lambda x:x[1], reverse=True)

    return [phrase for phrase, score in ranked_phrases[:3]]
