# Version 2 of Indeed-Web-Scraper
Python implementation to scrape job postings from Indeed. 

Modified version of main branch program.
Major differences include:
- Using Selenium and chromedriver to retrieve data instead of BeautifulSoup
- Insertion of data into mySQL environment
- Usage of text files to read in mySQL server login info (contained in a text file called "login.txt") as well as search parameters and necessary filenames. Included in jobSearches.txt.

