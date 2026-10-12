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
    print("Success!")
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

print(url)