import requests
from requests import get
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from searchMethods import advancedSearch
from multiprocessing import Pool


class indeed:

    def __init__(self):
        self.headers = {"Accept-Language": "en-US, en;q=0.5"}
        self.base_url = "https://www.indeed.com"
        self.search_start = "/jobs?q="
        self.query, self.printedOutput = "", "",
        self.results_endpoint = 10  # default value to get first page of results

        # Stores the queries that have already been added to the search url
        self.date, self.radius, self.remote, self.salary, self.location, self.experience_level = "", "", "", "", "", ""
        self.job_type, self.education = "", ""

        # This holds the user inputted keywords for constructing the search url
        self.keywords = []

        # These hold the data needed for the Pandas dataframe
        self.titles = []
        self.companies = []
        self.locations = []
        self.links = []
        self.salaries = []
        self.postDates = []
        self.descriptions = []
        self.types = []
        self.hireNumber = []

        self.jobDict = {}

    def prompt(self):

        # Prompts user for keywords
        keyword_input = input("Enter a job title you would like to retrieve open postings for: ")
        self.keywords = keyword_input.split(" ")
        self.urlPrep()

        # Prompts user to run search filter
        choice = input("Would you like to run an advanced search? Enter yes or no: ")
        if "yes" in self.ynInputCheck(choice):
            s = advancedSearch(self.base_url, self.search_start, self.query, self.search)
            self.search = s.advancedSearch()

        # Prompts user for amount of postings to get
        choice = input(
            "How many pages would you like to retrieve? Must be a positive number and keep in mind that a high number "
            "of pages may result in non-retrieval of data: ")
        while not choice.isdigit() or int(choice) <= 0 or not choice:
            choice = input("Invalid input. Please try again: ")
        self.results_endpoint = int(choice) * 10
        print(self.search)
        self.dataRetrieval()

    # Constructs the base search url from the keywords inputted
    def urlPrep(self):
        for word in self.keywords:
            if not self.query:
                self.query = word
            else:
                self.query += "%20" + word
        self.search = self.base_url + self.search_start + self.query

    # Multiple functions use this to check for a yes or no input
    def ynInputCheck(self, promptedInput):
        while (promptedInput.lower() not in ("yes", "no")) or not promptedInput.isalpha():
            promptedInput = input("Not a valid option. Enter yes or no: ").lower()
        return promptedInput

    # The retrieval function that gets all job postings within the indicated keywords and filters if any
    def dataRetrieval(self):
        # Loop through each retrieved structure and extract particular elements
        counter = 0
        for results_index in range(0, self.results_endpoint, 10):

            # Gets every page in the range indicated by the user
            results = requests.get(self.search + "&start=" + str(results_index), headers=self.headers)
            print(self.search + "&start=" + str(results_index))
            self.soup = BeautifulSoup(results.text, "html.parser")

            # This is the encompassing html class that contains all the data in each posting
            job_titles = self.soup.find_all('a', class_="tapItem")
            if job_titles:
                for title in job_titles:
                    dictEntry = []
                    # Get hyperlink of the posting
                    link = title.get("href")
                    # Since each posting has a distinct link, we can use this to filter out any duplicate postings
                    # Used for edge case where amount of job postings are less than pages indicated
                    if link in self.links:
                        break
                    else:
                        self.links.append(self.base_url + link)

                    # Get the title of the position
                    jobTitle = title.h2.text
                    # Some listings have "new" in the title, this removes them
                    job = jobTitle[3:] if ("new" in jobTitle) else jobTitle
                    self.titles.append(job)
                    dictEntry.append(job)

                    # Get the name of the company
                    companyName = title.find('span', class_='companyName').text if title.find('span',
                                                                                              class_='companyName') else '-'
                    self.companies.append(companyName)
                    dictEntry.append(companyName)

                    # Get location of company or job
                    companyLocation = title.find('div', class_='companyLocation').text
                    self.locations.append(companyLocation)

                    # Get estimated salary if it exists in the post
                    if title.find('div', attrs={'class': 'attribute_snippet'}):
                        salary = title.find('div', attrs={'class': 'attribute_snippet'})
                        for item in salary:
                            if '$' in item:
                                self.salaries.append(item)
                                dictEntry.append(item)
                                break
                        else:
                            self.salaries.append("No data to display")
                            dictEntry.append("No data to display")
                    else:
                        self.salaries.append("No data to display")
                        dictEntry.append("No data to display")

                    # Get the date posted of the listing
                    date = title.find('span', class_='date').text
                    dateValue = ' '.join(filter(lambda x: x.isdigit(), date))
                    dateNumber = "".join(dateValue.split(" "))
                    if "p" == date[0].lower():
                        if not dateNumber:
                            self.postDates.append("Today")
                            dictEntry.append("Today")
                        else:
                            if "3" in dateNumber and "0" in dateNumber:
                                self.postDates.append("30+ days ago")
                                dictEntry.append("30+ days ago")
                            else:
                                self.postDates.append(dateNumber + " day(s) ago")
                                dictEntry.append(dateNumber + " day(s) ago")
                    if "e" == date[0].lower():
                        self.postDates.append("Employer Active " + dateNumber + " day(s) ago")
                        dictEntry.append("Employer Active " + dateNumber + " day(s) ago")

                    # Elements to get when following a link
                    # p class=icl-u-xs-my--none
                    # Qualifications

                    # Get the description snippet in the post
                    description = title.find('li')
                    self.descriptions.append(description.text)
                    descriptionText = description.text if description.text else '-'
                    dictEntry.append(descriptionText)

                    #######################
                    self.jobDict[self.base_url + link] = dictEntry

                    individualResults = requests.get(self.base_url + link, headers=self.headers)
                    positionSoup = BeautifulSoup(individualResults.text, "html.parser")
                    position = positionSoup.find('div', attrs={'id': 'jobDetailsSection'})
                    jobType = ""
                    hireNumber = ""
                    if position is not None:
                        if position.text is not None:
                            position = position.text
                        jobType += "Full-time" if "Full-time" in position else "Part-time" if "Part-time" in position else "Internship" if "Internship" in position else "Contract" if "Contract" in position else "Temporary" if "Temporary" in position else "No data available"
                        if "hires" in position:
                            for index in range(len(position) - 1, 0, -1):
                                if not position[index].isalpha() or '+' in position[index]:
                                    hireNumber += position[index]
                                else:
                                    break
                            hireNumber = hireNumber[::-1]
                        else:
                            hireNumber += "No data to display"
                    else:
                        jobType += "No data to display"
                        hireNumber += "No data to display"
                    if hireNumber == "":
                        hireNumber = "On-going need to fill this role"
                    self.types.append(jobType.lstrip())
                    self.hireNumber.append(hireNumber.rstrip())
                    counter += 1
                    # Overarching class?
                    # div id="jobDetailsSection"
                    # class="jobSearch-jobDescriptionSection-section"

                    # Description in posting link
                    # div id="jobDescriptionText" class="jobSearch-jobDescriptionText"
                    # either this or try to find all text in the <p> tags

            # If nothing is returned either due to invalid search parameters or lack of data
            else:
                if not self.titles:
                    choice = input(
                        "Doesn't look like there are any results for that search. Would you like to try again? Enter yes or no: ").lower()
                    if "yes" in self.ynInputCheck(choice):
                        self.resetVariables()
                    else:
                        print("Goodbye")
                        exit(0)
                else:
                    break

        # Calls the console print function
        print(counter)
        self.printData()

        # Prompts the user to indicate whether to write to a file and/or if they want to run another search
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

    # Prints the retrieved data in a readable format to the console
    def printData(self):
        for i in range(len(self.titles)):
            self.printedOutput += "Job Title: " + self.titles[i] + "\n" + "Posted: " + self.postDates[
                i] + "\n" + "Company: " + self.companies[i] + "\n" + "Location(s): " + self.locations[
                                      i] + "\n" + "Job Type: " + self.types[
                                      i] + "\n" + "Number of Hires for this Role: " + self.hireNumber[
                                      i] + "\n" + "Estimated Salary: " + self.salaries[
                                      i] + "\n" + "Job Description Snippet: " + self.descriptions[
                                      i] + "\n" + "Job Link: " + self.links[i] + "\n\n"
        self.printedOutput.lstrip()
        print("\n" + self.printedOutput)

    # Contains the file writing operations that the user might like to do.
    # Currently supports exporting the html output and the printed output to both a text file and a .csv file via a Pandas dataframe
    def fileWrite(self):
        counter = 0
        choice = input("Would you like to write the retrieved html data to a file? ").lower()
        if "yes" in self.ynInputCheck(choice):
            writeBack = open(input("Enter a file name (just the name, not .txt): ") + ".txt", "wb")
            writeBack.write(bytes(self.soup.prettify(), 'utf-8'))
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

        print("Wrote to " + str(counter) + " files")

    # Function to clear all previously stored values in between searches
    def resetVariables(self):
        self.keywords.clear(), self.titles.clear(), self.companies.clear()
        self.locations.clear(), self.salaries.clear(), self.links.clear(), self.types.clear(), self.postDates.clear(), self.descriptions.clear()

        self.results_endpoint = 10
        self.query, self.printedOutput, self.job_type, self.education = "", "", "", ""
        self.date, self.radius, self.remote, self.salary, self.location, self.experience_level = "", "", "", "", "", ""

        self.prompt()

    # Contains the creation and formatting of the dataframe for exporting the data to a .csv
    def jobsPd(self):
        jobs = pd.DataFrame({
            'Job Title': self.titles,
            'Posted Date': self.postDates,
            'Company': self.companies,
            'Location(s)': self.locations,
            'Job Type': self.types,
            'Estimated Salary in $': self.salaries,
            'Job Description Snippet': self.descriptions,
            'Link to Posting': self.links,
        })
        jobs.index += 1

        jobs.to_csv(input("Enter a file name (just the name, not .csv): ") + '.csv')


# Entry point
if __name__ == "__main__":
    i = indeed()
    i.prompt()