import pandas as pd
from searchMethods import advancedIndeedSearch
from datetime import date, datetime
from multiprocessing.dummy import Pool
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from os.path import exists
import time
from db_mySQL import mySQL

# Handles all variables, objects, and methods relating to scraping jobs from Indeed.com and the
# subsequent storing of data as .csv files as well as passing of data to mySQL class


class indeed:

    def __init__(self):
        # Variables holding multiple components of the search url and various other components
        self.base_url = "https://www.indeed.com"
        self.search_start = "/jobs?q="
        self.pastDay = '&fromage=1'  # get jobs posted in the past 24 hours
        self.results_endpoint = 10  # default value to get first page of results
        self.searchText = []

        # Holds urls of the search url and any subsequent pages
        self.urls = []

        # Holds all listing data retrieved
        self.positions = []

        # Holds the mySQL class object
        self.sql = None

        # Holds the designated title of each table and the title of the .csv file
        self.tableTitle, self.fileTitle = '', ''

    # Constructs the mySQL object, reads the search text file and calls the url construction method to build the search urls
    def launchAndRead(self):
        self.sql = mySQL()
        self.sql.login()
        with open('jobSearches.txt', 'r') as f:
            for item in f:
                line = item.split(',')
                splitText = []
                for piece in line:
                    splitText.append(piece.strip())
                self.searchText.append(splitText)

        self.urlConstruction()

    # Builds the search urls with the necessary filter parameters
    def urlConstruction(self):
        for item in self.searchText:
            url = self.base_url + self.search_start + \
                str(item[0]) + str(item[1]) + self.pastDay
            self.fileTitle, self.tableTitle = str(item[2]), str(item[3])

            self.urlAdd(url)

    # Generates the necessary page urls from the choice indicated by the user
    def urlAdd(self, url):
        urlConstructs = []
        results_endpoint = 50
        for results_index in range(0, results_endpoint, 10):
            urlConstructs.append(
                url + "&start=" + str(results_index))

        self.multiProcess(urlConstructs)

    # Utilizes multithreading to retrieve multiple pages at once, reducing overall runtime
    def multiProcess(self, urls):

        pool = Pool(5)
        pool.map(self.scrape, urls)

        self.jobsPd()
        self.resetVariables()

    # Scraping function
    def scrape(self, url):
        opts = Options()
        opts.add_argument("--headless")
        driver = uc.Chrome(options=opts, use_subprocess=True)
        driver.get(url)
        time.sleep(10)

        jobs = driver.find_elements(
            By.CLASS_NAME, 'slider_container.css-g7s71f.eu4oa1w0')

        newPool = Pool(15)
        newPool.map(self.trawl, jobs)

    # Gets details of each posting retrieved
    def trawl(self, element):
        companyName, companyLocation = '', ''
        salary, description, link = '', '', ''
        try:
            jobTitle = element.find_element(
                By.CLASS_NAME, 'css-1m4cuuf.e37uo190')
            try:
                company = element.find_element(
                    By.CLASS_NAME, 'companyName')
                companyName = company.text
            except:
                companyName = 'No data available'
            try:
                location = element.find_element(
                    By.CLASS_NAME, 'companyLocation')
                companyLocation = location.text
            except:
                companyLocation = 'No data available'
            try:
                salary_And_Hours = element.find_element(
                    By.CLASS_NAME, 'heading6.tapItem-gutter.metadataContainer.noJEMChips.salaryOnly')
                salary = salary_And_Hours.text
            except:
                salary = 'No data available'
            try:
                desc = element.find_element(
                    By.CLASS_NAME, 'jobCardShelfContainer.big6_visualChanges')
                description = desc.text
            except:
                description = 'No data available'
            try:
                jobLink = element.find_element(
                    By.CLASS_NAME, 'jcs-JobTitle.css-jspxzf.eu4oa1w0')
                link = jobLink.get_attribute('href')
            except:
                link = 'No data available'
            self.positions.append([jobTitle.text, companyName, companyLocation,
                                  salary, description, link])
        # Only used if a post doesn't even have a job title
        except Exception as err:
            print(f"Error: '{err}'")
            return

    # Function to clear all previously stored values in between searches
    def resetVariables(self):
        self.positions.clear()
        self.fileTitle, self.tableTitle = '', ''

    # Contains the creation and formatting of the dataframe for exporting the data to a .csv
    # Also calls the mySQL object to insert the data into the respective SQL tables
    def jobsPd(self):
        jobs = None
        if self.positions:
            if exists(self.fileTitle + '.csv'):
                titles, companies, locations, salaries, descriptions, links = zip(
                    *self.positions)
                jobs = pd.DataFrame({
                    'Job Title': titles,
                    'Company': companies,
                    'Location(s)': locations,
                    'Salary and Hour Info': salaries,
                    'Job Description': descriptions,
                    'Link to Posting': links,
                    'Date Added to List': str(date.today()),
                    'Applied': 0,
                    'Interviewed': 0,
                    'Rejected': 0
                })
                jobs.index += 1
                jobs = jobs.drop_duplicates(keep='first')
                jobs.to_csv(self.fileTitle + '.csv', mode='a', header=False)
                with open('Operation Log.txt', 'a') as f:
                    f.write('Recorded new jobs in' + str(self.fileTitle) + '.csv @ ' +
                            str(datetime.now()) + '\n')
                self.sql.sql_insert(jobs, self.tableTitle)
            else:
                titles, companies, locations, salaries, descriptions, links = zip(
                    *self.positions)
                jobs = pd.DataFrame({
                    'Job Title': titles,
                    'Company': companies,
                    'Location(s)': locations,
                    'Salary and Hour Info': salaries,
                    'Job Description': descriptions,
                    'Link to Posting': links,
                    'Date Added to List': str(date.today()),
                    'Applied': 0,
                    'Interviewed': 0,
                    'Rejected': 0
                })
                jobs.index += 1
                jobs = jobs.drop_duplicates(keep='first')
                jobs.to_csv(self.fileTitle + '.csv')
                with open('Operation Log.txt', 'a') as f:
                    f.write('Recorded new jobs in' + str(self.fileTitle) + '.csv @ ' +
                            str(datetime.now()) + '\n')
                self.sql.sql_insert(jobs, self.tableTitle)
        else:
            with open('Operation Log.txt', 'a') as f:
                f.write('No new jobs to record in ' + self.fileTitle +
                        '@ ' + str(datetime.now()) + '\n')
