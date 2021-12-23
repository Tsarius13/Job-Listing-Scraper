from re import search


class advancedSearch:
    date, radius, remote, salary, location, experience_level = "", "", "", "", "", ""
    job_type, education = "", ""

    advOptions = ("date", "remote", "radius", "salary", "experience", "level", "experiencelevel", "location",
                  "job type", "type", "job", "education", "exit")
    searchRadius = str(("no", 0, 5, 10, 15, 25, 50, 100))
    states = (
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC,", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
        "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
        "OK", "OR", "PA", "PR", "RI", "SD", "SC", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY")
    dateSort = str(("no", 24, "24 hours", 3, "3 days", 7, "7 days", 14, "14 days"))
    level = ("entry", "mid", "senior")
    types = ("full", "full-time", "part", "part-time", "temporary", "contract", "internship")
    degrees = ("high", "school", "high school", "bachelor's", "master's", "associate's", "doctoral")

    def __init__(self, selfSearch):
        self.search = selfSearch

    def ynInputCheck(self, promptedInput):
        while (promptedInput.lower() not in ("yes", "no")) or not promptedInput.isalpha():
            promptedInput = input("Not a valid option. Enter yes or no: ").lower()
        return promptedInput

    def advancedSearch(self):
        choice = ""
        while ("exit" not in choice.lower()):
            choice = input(
                "Enter an advanced search option and keep in mind that each option can only search by one category at a time\n" +
                "The choices are by Date, Radius, Remote, Salary, Experience Level, Location, Job Type, Education, or enter exit to search: ")
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
                return self.search
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
                print("Date Tag Removed")
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
        print("Date Tag Added")

    # Filters results based on city and state
    def locationQuery(self):
        if self.location:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.location)
                self.location = ""
                print("Location Removed")
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
        print("Location Added")

    # Filters results based on search radius of the location
    def radiusQuery(self):
        if self.radius:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.radius)
                self.radius = ""
                print("Search Radius Removed")
                return
            else:
                self.filterRemoval(self.radius)

        choice = input(
            "Enter a radius in the set 0, 5, 10, 15, 25, 50, or 100 miles: ")
        while choice not in self.searchRadius or not choice:
            choice = input("Enter a radius in the set 0, 5, 10, 15, 25, 50 or 100 miles: ")

        self.radius = "&radius=" + choice
        self.search += self.radius
        print("Search Radius Added")

    # Flag to indicate searching for designated remote jobs
    def remoteQuery(self):
        if not self.remote:
            self.remote = "&remotejob=1"
            self.search += self.remote
            print("Remote Tag Added")
        else:
            choice = input("Would you like to remove the remote tag from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.remote)
                self.remote = ""
                print("Remote Tag Removed")

    # Filters results based on a user defined salary number
    def salaryQuery(self):
        if self.salary:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.salary)
                self.salary = ""
                print("Salary Tag Removed")
                return
            else:
                self.filterRemoval(self.salary)

        choice = input("Enter a number: ")
        while not choice.isdigit() or int(choice) <= 0 or not choice:
            choice = input("Not a valid number. Try again.  ")
        self.salary = "&salaryType=%24" + choice
        self.search += self.salary
        print("Salary Tag Added")

    # Filters results based on experience level
    def levelQuery(self):
        if self.experience_level:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.experience_level)
                self.experience_level = ""
                print("Experience Level Removed")
                return
            else:
                self.filterRemoval(self.experience_level)

        choice = input("Enter a choice in the set of entry, mid, or senior level: ")
        while not choice or not choice.isalpha() or choice not in self.level:
            choice = input("Not a valid input. Try again. ")
        choice = choice.lower()
        self.experience_level = "&explvl=" + choice + "_level"
        self.search += self.experience_level
        print("Experience Level Added")

    # Filters results based on the type of job
    def typeQuery(self):
        if self.job_type:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.job_type)
                self.job_type = ""
                print("Job Type Removed")
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
        print("Job Type Added")

    # Filters results based on education level
    def eduQuery(self):
        if self.education:
            choice = input("This filter already exists. Do you only want to remove the filter from your search? ")
            if "yes" in self.ynInputCheck(choice):
                self.filterRemoval(self.education)
                self.education = ""
                print("Education Level Removed")
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
        if "high" in choice or "school" in choice or "high school" in choice:
            self.education = "&education=" + "high_school_degree"
        else:
            self.education = "&education=" + choice + "_degree"
        self.search += self.education
        print('Education Level Added')