from abc import ABC,abstractmethod
import requests
import time

class APIBot(ABC):
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

class User(APIBot):
    def __init__(self, username, password, login_url, district, debug=True, delay=0):
        super().__init__(login_url, debug, delay)

        login_info = {
            "username" : username,
            "password" : password,
            "appName" : district,
        }

        self.api_request('POST', "verify.jsp", data=login_info, json=False)

        self.log("Login success.")

    def log(self, string):
        if self.debug:
            print(str(string))

    def api_request(self, method, url, params=None, data=None, files=None, json=True):
        result = super().api_request(method, url, params, data, files)
        return result.json() if json else result

    def getAllGrades(self, json=False):
        result = self.api_request('GET', "resources/portal/grades")
        return result if json else [User.Term(data) for data in result[0]['terms']]

    def getGrades(self):
        result = self.getAllGrades(json=True)[0]['terms']
        return User.Term(result[len(result) - 1])
        #may or may not work if user is not in last 6 weeks... i have no way of knowing until next school year

    def getSchedule(self):
        return self.api_request('GET', "resources/portal/roster")

    class Term:
        def __init__(self, term_data):
            self.id = term_data['termID']
            self.name = term_data['termName']
            self.number = term_data['termSeq']
            self.start_date = term_data['startDate']
            self.end_date = term_data['endDate']
            self.classes = [User.Course(course) for course in term_data['courses']]

    class Course:
        def __init__(self, course_data):
            self.name = course_data['courseName']
            self.number = course_data['courseNumber']
            self.room_name = course_data['roomName']
            self.teacher_name = course_data['teacherDisplay']
            if 'score' in course_data['gradingTasks'][0]:
                self.letter_grade = course_data['gradingTasks'][0]['score']
                self.grade = course_data['gradingTasks'][0]['percent']
            elif 'progressScore' in course_data['gradingTasks'][0]:
                self.letter_grade = course_data['gradingTasks'][0]['progressScore']
                self.grade = course_data['gradingTasks'][0]['progressPercent']
            else:
                self.letter_grade = None
                self.grade = None

def getDistrict(districtName, state):
    params = {"query": districtName, "state": state}
    result = requests.get("https://mobile.infinitecampus.com/mobile/searchDistrict", params=params).json()

    return [district['district_app_name'] for district in result['data']]
