# Infinite-Campus-API
Python tool to retrieve grades, schedule, and gradebook updates as objects or raw JSON  (WIP)

I tested this on my own account and it worked perfectly, but I'm not sure if it will work for all schools.

## How to use
All you need for this tool is your login info, your school's infinite campus page, and your school's district name

Go to your school's Infinite Campus login page and copy the URL from the beginning to the end of "campus" and include the '/' at the end.


Ex: https://domain.com/campus/

If you are not sure of your district code, you can use the getDistrict method. It will return a list of possible district codes for your area. The second parameter is the two letter abbreviation for your state
```python
districts = getDistrict("district name", "CO")
```

## Example
```python
student = User("username", "password", "https://domain.com/campus/", "district")
current_term = student.getGrades()
class1 = current_term.classes[0]

print(class1.letter_grade)
```

## Things to do
 - Make getSchudeule return objects instead of JSON
 - Add getGradebook option
 - Add function to get the unofficial transcript
 - Add function to get user data like name, school, picture, etc.
