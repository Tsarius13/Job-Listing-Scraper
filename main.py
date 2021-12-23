import requests
from requests import get
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from searchMethods import advancedSearch
from multiprocessing.dummy import Pool


class indeed:

    def __init__(self):
        # Variables holding multiple components of the search url, BeautfifulSoup input, and various other components
        self.headers = {"Accept-Language": "en-US, en;q=0.5"}
        self.base_url = "https://www.indeed.com"
        self.search_start = "/jobs?q="
        self.query, self.printedOutput = "", "Results of Search: \n",
        self.results_endpoint = 10  # default value to get first page of results

        # Holds the user inputted keywords for constructing the search url
        self.keywords = []

        # Holds urls of the search url and any subsequent pages
        self.urls = []

        # Holds all listing data retrieved
        self.positions = []

        # Holds the BeautifulSoup output of each scrape for exporting if desired
        self.soups = []

        # Used for checking duplicate hyperlinks
        self.links = set()

    def prompt(self):

        # Prompts user for keywords
        keyword_input = input("Enter a job title you would like to retrieve open postings for: ")
        self.keywords = keyword_input.split(" ")
        self.urlPrep()

        # Prompts user to run search filter, and if so, creates and calls the advancedSearch class object
        choice = input("Would you like to run an advanced search? Enter yes or no: ")
        if "yes" in self.ynInputCheck(choice):
            s = advancedSearch(self.search)
            self.search = s.advancedSearch()

        # Prompts user for amount of postings to get
        choice = input(
            "How many pages would you like to retrieve? Must be a positive number and keep in mind that a high number "
            "of pages may result in non-retrieval of data: ")
        while not choice.isdigit() or int(choice) <= 0 or not choice:
            choice = input("Invalid input. Please try again: ")
        self.urlAdd(choice)

    # Constructs the base search url from the keywords inputted
    def urlPrep(self):
        for word in self.keywords:
            if not self.query:
                self.query = word
            else:
                self.query += "%20" + word
        self.search = self.base_url + self.search_start + self.query

    # Generates the necessary page urls from the choice indicated by the user
    def urlAdd(self, choice):
        self.results_endpoint = int(choice) * 10
        for results_index in range(0, self.results_endpoint, 10):
            self.urls.append(self.search + "&start=" + str(results_index))
        self.multiProcess()

    # Utilizes multithreading to retrieve multiple pages at once, reducing overall runtime
    def multiProcess(self):
        results = requests.get(self.urls[0])
        self.soup = BeautifulSoup(results.text, "html.parser")

        # This is the encompassing html class that contains all the data in each posting
        job_titles = self.soup.find_all('a', class_="tapItem")
        if job_titles:
            pool = Pool(5)
            pool.map(self.scrape, self.urls)
            pool.terminate()
            pool.join()
            self.printData()
        else:
            choice = input(
                "Doesn't look like there are any results for that search. Would you like to try again? Enter yes or no: ").lower()
            if "yes" in self.ynInputCheck(choice):
                self.resetVariables()
            else:
                print("Goodbye")
                exit(0)

        choice = input("Would you like to write to a file? Enter yes or no: ").lower()
        if "yes" in self.ynInputCheck(choice):
            self.fileWrite()
            choice = input("Would you like to run another search? ").lower()
            if "yes" in self.ynInputCheck(choice):
                self.resetVariables()
            else:
                print("Goodbye")
                exit(0)
        else:
            choice = input("Would you like to run another search? ").lower()
            if "yes" in self.ynInputCheck(choice):
                self.resetVariables()
            else:
                print("Goodbye")
                exit(0)

    # Scraping function
    def scrape(self, url):
        results = requests.get(url)
        soup = BeautifulSoup(results.text, "html.parser")
        self.soups.append([url, soup])

        # This is the encompassing html class that contains all the data in each posting
        job_titles = soup.find_all('a', class_="tapItem")
        if job_titles:
            for title in job_titles:
                positionEntry = []

                # Get hyperlink of the posting
                link = title.get("href")
                # Since each posting has a distinct link, we can use this to filter out any duplicate postings
                # Used for edge case where amount of job postings are less than pages indicated
                jobLink = self.base_url + link
                if jobLink in self.links:
                    break
                else:
                    self.links.add(jobLink)
                    positionEntry.append(jobLink)

                # Get the title of the position
                jobTitle = title.h2.text
                # Some listings have "new" in the title, this removes them
                job = jobTitle[3:] if ("new" in jobTitle) else jobTitle
                positionEntry.append(job)

                # Get the name of the company
                companyName = title.find('span', class_='companyName').text if title.find('span',
                                                                                          class_='companyName') else '-'
                positionEntry.append(companyName)

                # Get location of company or job
                companyLocation = title.find('div', class_='companyLocation').text
                positionEntry.append(companyLocation)

                # Get estimated salary if it exists in the post
                salary = ""
                if title.find('div', attrs={'class': 'attribute_snippet'}):
                    salary = title.find('div', attrs={'class': 'attribute_snippet'})
                    for item in salary:
                        if '$' in item:
                            salary = item
                            break
                    else:
                        salary = "No data to display"

                positionEntry.append(salary)

                # Get the date posted of the listing
                date = title.find('span', class_='date').text
                dateValue = ' '.join(filter(lambda x: x.isdigit(), date))
                dateNumber = "".join(dateValue.split(" "))
                postDate = date
                if "p" == date[0].lower():
                    if not dateNumber:
                        postDate = "Today"
                    else:
                        if "3" in dateNumber and "0" in dateNumber:
                            postDate = "30+ days ago"
                        else:
                            postDate = dateNumber + " day(s) ago"
                if "e" == date[0].lower():
                    postDate = "Employer Active " + dateNumber + " day(s) ago"

                positionEntry.append(postDate)

                # This block is where each job link is visited to get information on the type of job, the number of
                # hires, and the full description of the position, if any such information exists
                individualResults = requests.get(self.base_url + link, headers=self.headers)
                positionSoup = BeautifulSoup(individualResults.text, "html.parser")
                position = positionSoup.find('div', attrs={'id': 'jobDetailsSection'})
                jobType = "No data to display"
                hireNumber = ""
                if position is not None:
                    if position.text is not None:
                        position = position.text
                        # There are only five types of jobs on Indeed
                    jobType = "Full-time" if "Full-time" in position else \
                        "Part-time" if "Part-time" in position else \
                            "Internship" if "Internship" in position else \
                                "Contract" if "Contract" in position else \
                                    "Temporary" if "Temporary" in position else "No data available"

                    # If number of hires is listed, it is always at the end of this html block,
                    # thus search from the end inwards
                    if "hires" in position:
                        for index in range(len(position) - 1, 0, -1):
                            if position[index].isdigit() or '+' in position[index]:
                                hireNumber += position[index]
                            else:
                                break
                        # Reverse the string to accurately display data
                        hireNumber = hireNumber[::-1]
                    else:
                        hireNumber = "No data to display"
                else:
                    hireNumber = "No data to display"
                if hireNumber == "":
                    hireNumber = "On-going need to fill this role"

                positionEntry.append(jobType)
                positionEntry.append(hireNumber.rstrip())

                position = positionSoup.find('div', attrs={'id': 'jobDescriptionText'})
                positionText = position.text if position else "No description available"
                positionEntry.append(positionText)

                # Add the position to the list of all positions
                self.positions.append(positionEntry)

                # Add to console print string
                self.printedOutput += "Job Title: " + job + "\n" + \
                                      "Posted: " + postDate + "\n" +\
                                      "Company: " + companyName + "\n" + \
                                      "Location(s): " + companyLocation + "\n" +\
                                      "Job Type: " + jobType + "\n" + \
                                      "Number of Hires for this Role: " + hireNumber + "\n" + \
                                      "Estimated Salary: " + salary + "\n" + \
                                      "Job Description: " + positionText + "\n" + \
                                      "Job Link: " + jobLink + "\n\n"

    # Console print function of resultant data
    def printData(self):
        print(self.printedOutput)

    # Multiple functions use this to check for a yes or no input
    def ynInputCheck(self, promptedInput):
        while (promptedInput.lower() not in ("yes", "no")) or not promptedInput.isalpha():
            promptedInput = input("Not a valid option. Enter yes or no: ").lower()
        return promptedInput

    # Contains the file writing operations that the user might like to do.
    # Currently supports exporting both the html output and the printed output to a text file and exporting the data to
    # a .csv file via a Pandas dataframe
    def fileWrite(self):
        counter = 0
        choice = input("Would you like to write the retrieved html data to a file? ").lower()
        if "yes" in self.ynInputCheck(choice):
            writeBack = open(input("Enter a file name (just the name, not .txt): ") + ".txt", "wb")
            for soup in self.soups:
                writeBack.write(bytes(soup[0] + "\n", 'utf-8'))
                writeBack.write(bytes(soup[1].prettify(), 'utf-8'))
                writeBack.write(bytes("\n", 'utf-8'))
            writeBack.close()
            counter += 1

        choice = input("Would you like to write the printed output to a file? Enter yes or no: ").lower()
        if "yes" in self.ynInputCheck(choice):
            writeBack = open(input("Input a file name (just the name, not .txt): ") + ".txt", "wb")
            writeBack.write(bytes(self.printedOutput, 'utf-8'))
            writeBack.close()
            counter += 1

        choice = input("Would you like to export the data to a .csv file? ").lower()
        if "yes" in self.ynInputCheck(choice):
            self.jobsPd()
            counter += 1

        print("Wrote to " + str(counter) + " file(s)")

    # Function to clear all previously stored values in between searches
    def resetVariables(self):
        self.keywords.clear(), self.urls.clear(), self.positions.clear(), self.links.clear()
        self.results_endpoint = 10
        self.query = ""
        self.prompt()

    # Contains the creation and formatting of the dataframe for exporting the data to a .csv
    def jobsPd(self):
        links, titles, companies, locations, salaries, postDates, types, hires, descriptions = zip(*self.positions)
        jobs = pd.DataFrame({
            'Job Title': titles,
            'Posted Date': postDates,
            'Company': companies,
            'Location(s)': locations,
            'Job Type': types,
            'Number of Hires': hires,
            'Estimated Salary in $': salaries,
            'Job Description': descriptions,
            'Link to Posting': links,
        })
        jobs.index += 1
        jobs.to_csv(input("Enter a file name (just the name, not .csv): ") + '.csv')


# Entry point
if __name__ == "__main__":
    i = indeed()
    i.prompt()