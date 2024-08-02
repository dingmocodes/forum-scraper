import bs_and_nlp
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class ThreadInfo:
    def __init__(self, title, url, date, views, replies, likes, phrases):
        self.title = title
        self.url = url
        self.date = date
        self.views = views
        self.replies = replies
        self.likes = likes
        self.phrases = phrases
    def __str__(self):
        return (
            f'Title: {self.title}\n'
            f'URL: {self.url}\n'
            f'Phrases: {self.phrases}\n'
            f'Date: {self.date}\n'
            f'Views: {self.views}\n'
            f'Replies: {self.replies}\n'
            f'Likes: {self.likes}\n'
            f'------------------'
        )
    
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_threads(forum, search_terms, num_results):
    driver = get_driver()

    # prepare the starting url
    start_url = ''
    if forum == 'Monzo':
        start_url = 'https://community.monzo.com/search?q='
    if forum == 'Emma':
        start_url = 'https://community.emma-app.com/search?q='
    if forum == 'Revolut':
        start_url = 'https://community.revolut.com/search?q='
    if forum == 'Fintech Forum':
        start_url = 'https://fintechforum.uk/search?q='
    search_split = search_terms.split(' ')
    for st in search_split[:-1]:
        start_url += st + '%20'
    start_url += search_split[-1]
    driver.get(start_url)

    # to scroll through the list of forums
    for i in range(1, (2 + int(num_results/50))):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

    # collecting all forum link elements
    thread_elements = driver.find_elements(By.CSS_SELECTOR, 'a.search-link')
    urls = []

    # collecting the actual forum urls
    for thread in thread_elements:
        urls.append(thread.get_attribute('href'))

    thread_list = []

    # collecting each forum's info
    for i in range(num_results):
        # to remove last section of URL
        url = urls[i]
        link_parts = url.split('/')
        link_topic = link_parts[4]
        link_id = link_parts[5]
        base_url = link_parts[0] + '//' + link_parts[2] + '/'
        thread_url = f"{base_url}t/{link_topic}/{link_id}"

        driver.get(thread_url)

        # obtain title
        title = driver.find_element(By.CSS_SELECTOR, "a.fancy-title").text

        # obtain date
        date_str = driver.find_element(By.CSS_SELECTOR, "a.widget-link.post-date span.relative-date").get_attribute('title')
        date_str = date_str.split()[0:3]
        date_str = " ".join(date_str)
        date_formats = ['%B %d, %Y', '%d %b %Y', '%Y-%m-%d']
        date = ''
        for fmt in date_formats:
            try:
                date = datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        # obtain views
        views_num = 0
        try:
            views_str = driver.find_element(By.CSS_SELECTOR, "span.number.heatmap-high").text
            views_num = float(views_str.split('k')[0]) * 1000
        except NoSuchElementException:
            try:
                views_str = driver.find_element(By.CSS_SELECTOR, "li.secondary.views span.number").text
                if len(views_str.split('k')) > 1:
                    views_num = float(views_str.split('k')[0]) * 1000
                else:
                    views_num = float(views_str)
            except NoSuchElementException:
                continue

        # obtain replies
        replies = 0
        try:
            replies = driver.find_element(By.CSS_SELECTOR, "li.replies span.number").text
        except NoSuchElementException:
            continue
        replies_split = replies.split('k')
        if len(replies_split) > 1:  # Ex. 14.3k
            replies = float(replies_split[0]) * 1000
        else:
            replies = float(replies)

        # obtain likes
        likes = 0
        try:
            likes = driver.find_element(By.CSS_SELECTOR, "li.secondary.likes span.number").text
        except NoSuchElementException:
            continue
        likes_split = likes.split('k')
        if len(likes_split) > 1:  # Ex. 14.3k
            likes = float(likes_split[0]) * 1000
        else:
            likes = float(likes)

        # obtain phrases
        phrases = bs_and_nlp.top_three_phrases(thread_url)
        tr = ThreadInfo(title, thread_url, date, views_num, replies, likes, phrases)
        thread_list.append(tr)

    driver.quit()
    return thread_list

def get_sorted(thread_list, sort_by, order):
    if sort_by == 'Title':
        if order == 'Ascending':
            return sorted(thread_list, key=lambda threads: threads.title)
        else:
            return sorted(thread_list, key=lambda threads: threads.title, reverse=True)
    if sort_by == 'Date':
        if order == 'Ascending':
            return sorted(thread_list, key=lambda threads: threads.date)
        else:
            return sorted(thread_list, key=lambda threads: threads.date, reverse=True)
    if sort_by == 'Views':
        if order == 'Ascending':
            return sorted(thread_list, key=lambda threads: threads.views)
        else:
            return sorted(thread_list, key=lambda threads: threads.views, reverse=True)
    if sort_by == 'Replies':
        if order == 'Ascending':
            return sorted(thread_list, key=lambda threads: threads.replies)
        else:
            return sorted(thread_list, key=lambda threads: threads.replies, reverse=True)
    if sort_by == 'Likes':
        if order == 'Ascending':
            return sorted(thread_list, key=lambda threads: threads.likes)
        else:
            return sorted(thread_list, key=lambda threads: threads.likes, reverse=True)
        
def get_attributes(thread_list, attribute):
    output = []
    if attribute == 'title':
        for tr in thread_list:
            output.append(getattr(tr, 'title'))
    if attribute == 'url':
        for tr in thread_list:
            output.append(getattr(tr, 'url'))
    if attribute == 'date':
        for tr in thread_list:
            output.append(getattr(tr, 'date'))
    if attribute == 'views':
        for tr in thread_list:
            output.append(getattr(tr, 'views'))
    if attribute == 'replies':
        for tr in thread_list:
            output.append(getattr(tr, 'replies'))
    if attribute == 'likes':
        for tr in thread_list:
            output.append(getattr(tr, 'likes'))
    if attribute == 'phrases':
        for tr in thread_list:
            output.append(getattr(tr, 'phrases'))
    return output
