import os
from pathlib import Path

from dataclasses import dataclass

#Strings
host = "www.successfactors.com"
entity = "PerPerson"

url = f"{host}/{entity}"
##print(url)

#-----------------------------------------------------------------
#Lists
a="1,2,3,4,5"
b=a.split(",")
#print(b[0])

b.append("6")
#print(b)

#-----------------------------------------------------------------
#Dictionaries
user1 = {"name": "John", "age": 30, "city": "New York"}
#print(user["name"])

user1["age"]=31
user1["city"]="Los Angeles"
user1["name"]="Jane"
#print(user1["name"])

user2 = {"name": "Alice", "age": 25, "city": "Chicago"}
#print(user2["name"])

#List of Dictionaries
user=[user1, user2]
#print (user)

#-----------------------------------------------------------------
#loops
modules = ["Employee Central", "Onboarding", "Compensation"]

#for module in modules:
    #print(module)

#-----------------------------------------------------------------
#loops a dictionary
user = {"name": "John", "age": 30, "city": "New York"}
#for key, value in user.items():
    #print(key, value)


#-----------------------------------------------------------------
#Loop in List of dictionaries
response = {
    "d": {
        "results": [
            {"userId": "1001", "email": "a@example.com"},
            {"userId": "1002", "email": "b@example.com"}
        ]
    }
}

#for user in response["d"]["results"]:    
    #print(user["userId"], user["email"])


#-----------------------------------------------------------------
#If-Else
status_code = 200

if status_code == 200:
    a=1
    #print("Success!")
elif status_code == 401:
    print("Authentication failed")
else:
    print(f"Something else happened: {status_code}")


#-----------------------------------------------------------------
#functions
def build_url(host, entity):
    return f"{host}/{entity}"

host = "www.successfactors.com"    
entity = "PerPerson"
url = build_url(host, entity)

#print(url)


#build token url
def build_token_url(host : str) -> str:
    if not str(host).startswith("https://"):
        return f"https://{host}/oauth/token"
    else:
        return f"{host}/oauth/token"

host = "https://www.successfactors.com"
#print(build_token_url(host))


#-----------------------------------------------------------------
#functions with dictionary
def build_user_dict(name, age, city) -> dict:
    new_user = {"name": name, "age": age, "city": city}
    return new_user

name = "John"
age = 30
city = "New York"
user = build_user_dict(name, age, city)
#print(user)


#-----------------------------------------------------------------
#Errors

user={"name": "John", "age": 30, "city": "New York"} # This will raise a NameError because name, age, and city are not defined as variables. They should be strings.
#print(user["name1"]) # This will raise a KeyError because "name1" is not a key in the user dictionary.


try:
    user={"name": "John", "age": 30, "city": "New York"}
    #print(user["name1"]) # This will raise a KeyError because "name1" is not a key in the user dictionary.
except KeyError as exe:\
    a=1
    #print(f"KeyError: {exe}")

#-----------------------------------------------------------------
#Path

p = Path("~/Documents/.stignore").expanduser()
#print(p)
#print(p.parent)
#print(p.name)
#print(p.suffix)
#print(p.exists())
#print(p.is_absolute())


#-----------------------------------------------------------------
#Environment Variables
#print(os.environ.get('HOME'))
#print(os.environ["HOME"])

#-----------------------------------------------------------------
#Classes
# __init__ method to initialize the class
# __repr__ method to return a string representation of the class

@dataclass #this automatically generates the __init__ and __repr__ methods for the class
class SFurl:
    host: str
    url: str

    #def __init__(self, host: str, url: str):
        #self.host = host
        #self.url = url

#print(SFurl("www.successfactors.com", "PerPerson"))
print(SFurl.__repr__(self))
