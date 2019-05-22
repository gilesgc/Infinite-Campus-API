# Infinite-Campus-API
Python tool to retrieve grades, schedule, and gradebook updates as objects or raw JSON  (WIP)

I tested this on my own account and it worked perfectly, but I'm not sure if it will work for all schools.

## How to use
All you need for this tool is your login info and your school's infinite campus page URL

Go to your school's Infinite Campus login page and copy the URL. If there are parameters, don't copy them. (i.e. if there is a question mark don't copy it or anything after)

If the bot is unable to find your district, you can use the getDistrict method. It will return a list of possible district codes for your area. The first parameter should be the first 4 or 5 letters of your district name. The second parameter is the two letter abbreviation for your state
```python
districts = icapi.getDistrict("district name", "CO")
```

## Example
```python
student = User("username", "password", "https://schoolwebsite.com/campus/district.jsp")
current_term = student.getGrades()
class1 = current_term.classes[0]

print(class1.letter_grade)
```

## Things to do
 - Make getSchudeule return objects instead of JSON
 - ~~Add getGradebook option~~
 - Add function to get the unofficial transcript
 - Add function to get user data like name, school, picture, etc.
