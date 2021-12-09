import requests
from requests import get
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
from re import search

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

        # Should we add company rating?
        # span class = "ratingsDisplay withRatingLink"
        # a aria-label = "Company rating..."

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

        # Sets needed to check input against accepted values
        self.advOptions = ("date", "remote", "radius", "salary", "experience", "level", "experiencelevel", "location",
                           "job type", "type", "job", "education", "exit")
        self.searchRadius = str(("no", 0, 5, 10, 15, 25, 50, 100))
        self.states = (
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC,", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
            "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
            "OK", "OR", "PA", "PR", "RI", "SD", "SC", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY")
        self.dateSort = str(("no", 24, 3, 7, 14))
        self.level = ("entry", "mid", "senior")
        self.types = ("full", "full-time", "part", "part-time", "temporary", "contract", "internship")
        self.degrees = ("high", "school", "high school", "bachelor's", "master's", "associate's", "doctoral")

    def prompt(self):

        # Prompts user for keywords
        keyword_input = input("Enter a job title you would like to retrieve open postings for: ")
        self.keywords = keyword_input.split(" ")
        self.urlPrep()

        # Prompts user to run search filter
        choice = input("Would you like to run an advanced search? Enter yes or no: ")
        if "yes" in self.ynInputCheck(choice):
            self.advancedSearch()

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

    # Search filter driver function
    def advancedSearch(self):
        choice = ""
        while ("exit" not in choice.lower()):
            choice = input(
                "Enter an advanced search option\n" + "The choices are by Date, Radius, Remote, Salary, Experience Level, "
                                                      "Location, Job Type, Education, "
                                                      "or enter exit to search: ")
            # Entering a query with multiple words is somehow not recognized
            while not choice.isalpha() or not choice or choice.lower().replace(" ", "") not in self.advOptions:
                choice = input("Not a valid option. If your choice is multiple words, try just entering one of them: ")
            choice = choice.lower()
            # Match against the different supported filters in Indeed.com
            if "date" in choice:
                self.dateQuery()
            elif "radius" in choice:
                self.radiusQuery()
            elif "remote" in choice:
                self.remoteQuery()
            elif "salary" in choice:
                self.salaryQuery()
            elif search("experience", choice) or search("level", choice) or choice.replace(" ", "") in (
            "experience", "level"):
                self.levelQuery()
            elif "location" in choice:
                self.locationQuery()
            elif "job" in choice or "type" in choice:
                self.typeQuery()
            elif "education" in choice:
                self.eduQuery()
            elif "exit" in choice:
                break
            else:
                pass

    # Search filter removal function
    def filterRemoval(self, query):
        tempSearch = self.search.replace(query, "")
        self.search = tempSearch

    # Filters results based on listing timeframes
    def dateQuery(self):
        if self.date:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                    self.filterRemoval(self.date)
                    self.date = ""
                    return
            else:
                self.filterRemoval(self.date)

        choice = input(
            "The options are past 24 hours, 3 days, 7 days, and 14 days: ")
        while choice not in self.dateSort or not choice:
            choice = input("Enter a valid time period to search by: ")

        self.date = "&fromage="
        if "24" == choice:
            self.date += "0"
        else:
            self.date += choice
        self.search += self.date

    # Filters results based on city and state
    def locationQuery(self):
        if self.location:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.location)
                self.location = ""
                return
            else:
                self.filterRemoval(self.location)

        city = input("Enter a city: ").lower().split(" ")
        while not city:
            city = input("Enter a city: ").lower().split(" ")
        state = input("Enter the state's abbrevation: ").upper()
        while state not in self.states or not state:
            state = input("Not a valid state. Try again: ")

        self.location = "&l="
        for item in city:
            if self.location == "&l=":
                self.location += item
            else:
                self.location += "%20" + item

        self.location += "%2C" + state
        self.location = self.location.lstrip()
        self.search += self.location

    # Filters results based on search radius of the location
    def radiusQuery(self):
        if self.radius:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.radius)
                self.radius = ""
                return
            else:
                self.filterRemoval(self.radius)

        choice = input(
            "Enter a radius in the set 0, 5, 10, 15, 25, 50, or 100: ")
        while choice not in self.searchRadius or not choice:
            choice = input("Enter a radius in the set 0, 5, 10, 15, 25, 50 or 100: ")

        self.radius = "&radius=" + choice
        self.search += self.radius
    # Flag to indicate searching for designated remote jobs
    def remoteQuery(self):
        if not self.remote:
            self.remote = "&remotejob=1"
            self.search += self.remote
        else:
            choice = input("Would you like to remove the remote tag from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.remote)
                self.remote = ""
        print("Done")

    # Filters results based on a user defined salary number
    def salaryQuery(self):
        if self.salary:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.salary)
                self.salary = ""
                return
            else:
                self.filterRemoval(self.salary)

        choice = input("Enter a number: ")
        while not choice.isdigit() or int(choice) <= 0 or not choice:
            choice = input("Not a valid number. Try again.  ")
        self.salary = "&salaryType=%24" + choice
        self.search += self.salary

    # Filters results based on experience level
    def levelQuery(self):
        if self.experience_level:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.experience_level)
                self.experience_level = ""
                return
            else:
                self.filterRemoval(self.experience_level)

        choice = input("Enter a choice in the set of entry, mid, or senior level: ")
        while not choice or not choice.isalpha() or choice not in self.level:
            choice = input("Not a valid input. Try again. ")
        choice = choice.lower()
        self.experience_level = "&explvl=" + choice + "_level"
        self.search += self.experience_level

    # Filters results based on the type of job
    def typeQuery(self):
        if self.job_type:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.job_type)
                self.job_type = ""
                return
            else:
                self.filterRemoval(self.job_type)

        choice = input("Enter a job type in the set of Full-time, Part-time, Temporary, Contract, or Internship:  ")
        while choice.lower() not in self.types:
            choice = input("Not a valid option. Try again. ")
        if "-" in choice:
            noDash = choice.replace("-", "")
            choice = noDash
        self.job_type = "&jt=" + choice.lower()
        self.search += self.job_type

    # Filters results based on education level
    def eduQuery(self):
        if self.education:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.education)
                self.education = ""
                return
            else:
                self.filterRemoval(self.education)

        choice = input(
            "Enter an education level in the set of High School, Associate's, Bachelor's, Master's, or Doctoral degrees: ")
        while choice.lower() not in self.degrees:
            choice = input("Not a valid degree. Try again. ")
        choice = choice.lower()
        if "'s" in choice:
            temp = choice.replace("'s", "")
            choice = temp
        # Trying to account for multiple word input here with no luck
        if "high" in choice or "school" in choice or "high school" in choice:
            self.education = "&education=" + "high_school_degree"
        else:
            self.education = "&education=" + choice + "_degree"
        self.search += self.education

    # The retrieval function that gets all job postings within the indicated keywords and filters if any
    def dataRetrieval(self):
        # Loop through each retrieved structure and extract particular elements
        for results_index in range(0, self.results_endpoint, 10):

            # Gets every page in the range indicated by the user
            results = requests.get(self.search + "&start=" + str(results_index), headers=self.headers)
            self.soup = BeautifulSoup(results.text, "html.parser")

            # This is the encompassing html class that contains all the data in each posting
            job_titles = self.soup.find_all('a', class_="tapItem")
            if job_titles:
                for title in job_titles:

                    # Get hyperlink of the posting
                    link = title.get("href")
                    # Since each posting has a distinct link, we can use this to filter out any duplicate postings
                    # Used for edge case where amount of job postings are less than pages indicated
                    if link in self.links:
                        flag = True
                        break
                    else:
                        self.links.append(self.base_url + link)

                    # Get the title of the position
                    jobTitle = title.h2.text
                    # Some listings have "new" in the title, this removes them
                    if ("new" in jobTitle):
                        job = jobTitle[3:]
                        self.titles.append(job)
                    else:
                        self.titles.append(jobTitle)

                    # Get the name of the company
                    companyName = title.find('span', class_='companyName').text if title.find('span',
                                                                                              class_='companyName') else '-'
                    self.companies.append(companyName)

                    # Get location of company or job
                    companyLocation = title.find('div', class_='companyLocation').text
                    self.locations.append(companyLocation)

                    # Get estimated salary if it exists in the post
                    if title.find('div', attrs={'class': 'attribute_snippet'}):
                        salary = title.find('div', attrs={'class': 'attribute_snippet'})
                        for item in salary:
                            if '$' in item:
                                self.salaries.append(item)
                                break
                        else:
                            self.salaries.append("Not available")
                    else:
                        self.salaries.append("Not available")

                    # Get the date posted of the listing
                    date = title.find('span', class_='date').text
                    dateValue = ' '.join(filter(lambda x: x.isdigit(), date))
                    dateNumber = "".join(dateValue.split(" "))
                    if "p" == date[0].lower():
                        if not dateNumber:
                            self.postDates.append("Today")
                        else:
                            if "3" in dateNumber and "0" in dateNumber:
                                self.postDates.append("30+ days ago")
                            else:
                                self.postDates.append(dateNumber + " day(s) ago")
                    if "e" == date[0].lower():
                        self.postDates.append("Employer Active " + dateNumber + " day(s) ago")

                    # Get the description snippet in the post
                    description = title.find('li')
                    self.descriptions.append(description.text)

                if flag == True:
                    break
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
        self.locations.clear(), self.salaries.clear(), self.links.clear(), self.postDates.clear(), self.descriptions.clear()

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
            'Estimated Salary in $': self.salaries,
            'Job Description Snippet': self.descriptions,
            'Link to Posting': self.links,
        })

        jobs.to_csv(input("Enter a file name (just the name, not .csv): ") + '.csv')


# Entry point
if __name__ == "__main__":
    i = indeed()
    i.prompt()