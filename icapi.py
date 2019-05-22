from abc import ABC,abstractmethod
import requests
import time
from bs4 import BeautifulSoup
import datetime

class RestClient(ABC):
    def __init__(self, api_url, debug=True, delay=0):
        self.api_url = api_url
        self.debug = debug
        self.delay = delay
        self.session = requests.Session()

    def api_request(self, method, url, params=None, data=None, files=None):
        time.sleep(self.delay)
        return self.session.request(method, self.api_url + url, params=params, data=data, files=files)

    @abstractmethod
    def log(self, string):
        pass

class User(RestClient):
    def __init__(self, username, password, login_url, district=None, debug=True, delay=0):
        super().__init__(login_url, debug, delay)

        self.api_url = self._get_api_url(login_url)

        if district is None:
            self.log("No district given. Attempting to find one...")
            login_page = self.session.get(login_url)
            district = BeautifulSoup(login_page.text, "html.parser").find("input", {'name': 'appName'})['value']
            self.log("Found district \"{}\"".format(district))

        login_info = {
            "username" : username,
            "password" : password,
            "appName" : district,
        }

        self.log("Logging in...")

        self.api_request('POST', "verify.jsp", data=login_info, json=False)

        if 'XSRF-TOKEN' in self.session.cookies:
            self.log("Login success.")
        else:
            raise Exception("Login failed.")

    def log(self, string):
        if self.debug:
            print("[*] {}".format(string))

    def api_request(self, method, url, params=None, data=None, files=None, json=True):
        result = super().api_request(method, url, params, data, files)
        return result.json() if json else result

    def _get_api_url(self, url):
        return url.split("campus/")[0] + "campus/"

    def getAllGrades(self, json=False):
        result = self.api_request('GET', "resources/portal/grades")
        self.log("Retrieved grades for all terms")
        return result if json else [User.Term(data) for data in result[0]['terms']]

    def getGrades(self):
        result = self.getAllGrades(json=True)[0]['terms']
        self.log("Retrieved grades for latest term")
        return User.Term(result[len(result) - 1])
        #may or may not work if user is not in last 6 weeks... i have no way of knowing until next school year

    def getGradebook(self, startDate=None, json=False):
        if startDate is None:
            today = datetime.date.today()
            startDate = today + datetime.timedelta(weeks=-2)

        if isinstance(startDate, datetime.date):
            date = startDate.strftime("%Y-%m-%d")
        elif isinstance(startDate, tuple):
            date = "{}-{}-{}".format(startDate[0], startDate[1], startDate[2])
        else:
            date = startDate

        params = {
            "modifiedDate|gte" : date,
            "_expand" : ["scores", "submission"]
        }
        
        result = self.api_request('GET', "resources/portal/assignment", params=params)
        items = [User.GradebookItem(item) for item in result]
        items.sort(key=lambda x: x.modified_date, reverse=True)
        return items

    def getSchedule(self):
        self.log("Retrieved schedule")
        return self.api_request('GET', "resources/portal/roster")

    class Term:
        def __init__(self, term_data):
            self.id =           term_data['termID']
            self.name =         term_data['termName']
            self.number =       term_data['termSeq']
            self.start_date =   term_data['startDate']
            self.end_date =     term_data['endDate']
            self.classes =      [User.Course(course) for course in term_data['courses']]

    class Course:
        def __init__(self, course_data):
            self.name =         course_data['courseName']
            self.number =       course_data['courseNumber']
            self.room_name =    course_data['roomName']
            self.teacher_name = course_data['teacherDisplay']

            grade = course_data['gradingTasks'][0]
            if 'score' in grade:
                self.letter_grade = grade['score']
                self.grade =        grade['percent']
            elif 'progressScore' in grade:
                self.letter_grade = grade['progressScore']
                self.grade =        grade['progressPercent']
            else:
                self.letter_grade = None
                self.grade =        None

    class GradebookItem:
        def __init__(self, grade_data):
            self.name =             grade_data['assignmentName']
            self.due_date =         grade_data['dueDate']
            self.assigned_date =    grade_data['assignedDate']
            self.modified_date =    grade_data['modifiedDate']
            self.course_name =      grade_data['courseName']
            self.teacher_name =     grade_data['teacherDisplay']

            score_data = grade_data['scores'][0]
            self.is_late =          score_data['late']
            self.is_incomplete =    score_data['incomplete']
            self.is_dropped =       score_data['dropped']
            self.is_missing =       score_data['missing']
            self.is_exempt =        score_data['exempt']
            self.is_turned_in =     score_data['turnedIn']
            self.score =            score_data['score'] if 'score' in score_data else None
            self.percentage =       score_data['scorePercentage'] if 'scorePercentage' in score_data else None
            self.total_points =     score_data['totalPoints']
            self.category =         score_data['category']
            self.weight =           score_data['weight']
            self.multiplier =       score_data['multiplier']


def getDistrict(districtName, state):
    params = {"query": districtName, "state": state}
    result = requests.get("https://mobile.infinitecampus.com/mobile/searchDistrict", params=params).json()

    return [district['district_app_name'] for district in result['data']]
