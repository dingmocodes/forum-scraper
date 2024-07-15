# Forum Scraper
This scraper is made to work on forums powered by discourse. By typing in one or more search terms, users can extract and sort key information from a number of posts. Current scrapable forums: Monzo, Emma, Revolut, Fintech Forum.

Deployed w/ Streamlit: https://forumscraper.streamlit.app/

## How it's made
### Tech used: Python, Selenium, Beautiful Soup, NLTK, Streamlit
This was made with Python and a combination of several libraries to accomplish the scraping. Selenium was used for web automation and extracting the links and key information. Beautiful Soup combined with NLTK enabled the ability to parse words in every post and return phrases with highest sentiment. With Streamlit, creating the frontend and deploying the app was seamless.

## Notes
In retrospect, one could opt out of using Beautiful Soup as Selenium has all the necessary functions to extract text from posts.
