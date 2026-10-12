---
title: "Learn Python by Building a SAP SuccessFactors Connection"
tags:
  - python
  - beginner
  - sap-successfactors
  - oauth2
  - saml
  - vscode
  - learning
---

```table-of-contents
title: 
style: nestedList # TOC style (nestedList|nestedOrderedList|inlineFirstLevel)
minLevel: 0 # Include headings from the specified level
maxLevel: 0 # Include headings up to the specified level
include: 
exclude: 
includeLinks: true # Make headings clickable
hideWhenEmpty: false # Hide TOC if no headings are found
debugInConsole: false # Print debug info in Obsidian console
```

# Learn Python by Building a SAP SuccessFactors Connection

Goal: learn Python from zero, while building something you actually want — a program that authenticates to SuccessFactors and pulls data from an OData API.

This document assumes **you have never written a line of Python**. Every concept is introduced when the project needs it, with something runnable at each step.

## How to use this document

Work through it in order, top to bottom. Don't skip ahead to the SAP parts.

Every section has a **Try it** box. Actually type the code — don't copy-paste, and don't just read. Typing it is how your fingers learn the syntax, and the typos you make teach you to read error messages, which is most of what programming is.

Expect roughly: Parts 1–2 in an evening, Part 3 over a few sessions, Parts 4–6 slower because the concepts are genuinely new.

> [!NOTE]
> There is a companion document, [03-python-sf-oauth-saml-bearer.md](03-python-sf-oauth-saml-bearer.md), with the same project written the way a professional Python developer would write it. Don't read it yet. Come back to it when you finish this one — seeing the same program twice, beginner version then polished version, is one of the fastest ways to level up.

## What you're building

```
   Your Fedora machine                        SuccessFactors
   ───────────────────                        ──────────────

   1. Build a SAML assertion   ──┐
      (an XML document saying      │
       "I am this user")           │
                                   │
   2. Sign it with a private key   │
      (proves it's really you)     │
                                   ▼
   3. Send it to SF  ──────────────────────►  "Here's my proof"
                                                     │
   4.                        ◄──────────────────  "OK, here's an
                                                   access token"
   5. Call the API with that token ─────────►  "Here's your data"
```

Five steps. We'll build them one at a time, in order, and each one works before we start the next.

---

# Part 1 — Getting set up

## 1. Install Python

Fedora already has Python. Open a terminal and check:

```bash
python3 --version
```

You should see something like `Python 3.12.x`. If not:

```bash
sudo dnf install -y python3 python3-pip
```

- `sudo` — run as administrator. Installing software needs it.
- `dnf install` — Fedora's software installer.
- `-y` — answer "yes" to the confirmation question automatically.
- `python3` — the Python program itself.
- `python3-pip` — a tool for installing extra Python libraries. We'll use it in Part 3.

> [!TIP]
> Always type `python3`, not `python`. On Linux, plain `python` can point somewhere unexpected. `python3` always means what you think it means.

## 2. Install VS Code

**Use Visual Studio Code.** It's free, it's the most common Python editor, and critically for you, its Git integration is the best of any editor. You'll be able to do most of what's in [04-git-concepts-to-advanced.md](04-git-concepts-to-advanced.md) by clicking instead of typing, while still seeing which command it ran.

Install it from Microsoft's official Fedora repository, then open it.

### Why VS Code over the alternatives

| Editor | Verdict |
|---|---|
| **VS Code** | **Recommended.** Free, lightweight, superb Git panel, huge extension library, the editor most tutorials assume |
| PyCharm Community | Also free and genuinely excellent for Python. Heavier, and its Git view is good but less immediate than VS Code's |
| Vim / nano | Fine for editing a config file over SSH. A painful way to learn a language |
| Jupyter notebooks | Great for data analysis, wrong shape for building an application |

### Extensions to install

Click the Extensions icon in the left sidebar (four squares), search for each, click Install:

1. **Python** (by Microsoft) — runs your code, debugging, interpreter selection.
2. **Pylance** (by Microsoft) — autocomplete and error detection as you type. This one will teach you a lot by catching mistakes before you run anything.
3. **GitLens** — shows who changed each line and when, inline. Hugely useful once you have history.

## 3. VS Code's Git integration — a quick tour

This is why you picked this editor. The **Source Control** panel is the third icon down in the left sidebar (a branching symbol).

| In VS Code | The command it runs |
|---|---|
| Changed files listed under "Changes" | `git status` |
| Click a file to see a side-by-side diff | `git diff` |
| `+` next to a file | `git add <file>` |
| Type a message, click the ✓ (Commit) | `git commit -m "..."` |
| "Sync Changes" button | `git pull` then `git push` |
| Branch name in the bottom-left corner | `git branch` — click it to switch |
| Coloured bars in the left margin of the editor | Lines you've added, changed, or deleted since the last commit |
| GitLens text at the end of a line | `git blame` for that line |

There's also a built-in terminal: **Terminal → New Terminal**, or `` Ctrl+` ``. It opens already inside your project folder. Use it for the `python3` and `git` commands in this document.

> [!TIP]
> Use the buttons at first. But glance at the **Output → Git** panel occasionally to see the actual commands. That's how the clicking turns into understanding, and why doc 04 stays useful.

## 4. Make your project folder

In the terminal:

```bash
mkdir -p ~/projects/sf-oauth
cd ~/projects/sf-oauth
code .
```

- `mkdir` — make directory. `-p` creates parent folders if missing and doesn't complain if it already exists.
- `~` — shorthand for your home folder, `/home/yourname`.
- `cd` — change directory. Move into the folder you just made.
- `code .` — open VS Code in the current folder. The `.` means "here".

VS Code opens with your (empty) project. Everything from now on happens in here.

---

# Part 2 — Python from zero

Six short sections. Create one file, run it, change it, run it again.

## 5. Your first program

In VS Code: **File → New File**, save it as `hello.py` inside your project folder.

```python
print("Hello from Python!")
```

Run it in the terminal:

```bash
python3 hello.py
```

Output:

```text
Hello from Python!
```

What happened: `print(...)` is a **function** — a named thing that does a job. You give it something inside the brackets, and it displays it. The quotes mark where the text starts and ends.

> [!TIP]
> You can also click the ▶ Run button in VS Code's top right. Same thing, fewer keystrokes.

### Try it
Change the message. Add a second `print` line. Run again. Notice both lines appear, in order, top to bottom. **Python runs your file one line at a time, from the top.** That's the whole execution model.

## 6. Variables — giving things names

```python
name = "Kriba"
company = "ACME"

print(name)
print(company)
```

```text
Kriba
ACME
```

- `=` means "store this value under this name". It does **not** mean "equals" in the maths sense.
- Read `name = "Kriba"` as: *"name, from now on, refers to Kriba."*

You can change what a name refers to:

```python
count = 1
print(count)
count = 2
print(count)
```

```text
1
2
```

### Naming rules
- Letters, numbers, underscores. No spaces, can't start with a number.
- Lowercase with underscores by convention: `company_id`, `access_token`, `user_name`.
- Case matters. `Name` and `name` are two different things.

### Try it
Make variables for `user_id` and `api_host`, and print them.

## 7. Types — text, numbers, true/false

Python values have **types**. The three you need now:

```python
company = "ACME"        # str   — text, always in quotes
timeout = 30            # int   — whole number, no quotes
rate = 1.5              # float — decimal number
is_active = True        # bool  — True or False (capital letter!)
```

- `#` starts a **comment**. Python ignores everything after it on that line. Comments are for humans.

Why types matter — this trips up everyone once:

```python
print(2 + 3)        # 5     — numbers add
print("2" + "3")    # 23    — text joins together
```

Those are completely different operations. The quotes are the whole difference.

Check a type when you're unsure:

```python
print(type(30))        # <class 'int'>
print(type("30"))      # <class 'str'>
```

Convert between them:

```python
text_number = "30"
real_number = int(text_number)     # now it's 30, a number
back_to_text = str(real_number)    # now it's "30", text again
```

### Try it
Run `print("5" + 5)`. You'll get a `TypeError`. **Read the error message.** It says you can't join text and a number. This is Python being helpful, not broken. Fix it with `int("5") + 5`.

## 8. Strings — working with text

Almost everything in this project is text: URLs, XML, tokens. So strings matter.

**f-strings** are the modern way to build text from variables. Put `f` before the opening quote, then put variable names inside `{}`:

```python
host = "api.example.com"
user = "api_user"

url = f"https://{host}/oauth/token"
print(url)

message = f"Connecting as {user} to {host}"
print(message)
```

```text
https://api.example.com/oauth/token
Connecting as api_user to api.example.com
```

Without the `f`, the braces stay as literal text. Try it and see — that's a mistake you'll make a few times.

Useful things strings can do:

```python
text = "  Hello World  "

print(text.strip())           # "Hello World"  — remove surrounding spaces
print(text.upper())           # "  HELLO WORLD  "
print(len("ACME"))            # 4              — how many characters
print("Hello".startswith("He"))   # True
print("a,b,c".split(","))     # ['a', 'b', 'c'] — split into a list
```

- `text.strip()` — the dot means "do this thing to `text`". Everything in Python works this way: `thing.action()`.

### Try it
Build a URL from two variables using an f-string. Then print its length with `len()`.

## 9. Lists and dictionaries — holding several things

### Lists — ordered items

```python
modules = ["Employee Central", "Onboarding", "Compensation"]

print(modules[0])        # Employee Central  — counting starts at ZERO
print(modules[1])        # Onboarding
print(len(modules))      # 3

modules.append("PMGM")   # add to the end
print(modules)
```

**Counting starts at 0.** The first item is `[0]`, the second is `[1]`. This catches everyone. The last item is `[-1]`.

### Dictionaries — labelled items

This is the most important one for this project. Every response from SuccessFactors arrives as a dictionary.

```python
user = {
    "username": "api_user",
    "company": "ACME",
    "active": True
}

print(user["username"])     # api_user
print(user["company"])      # ACME
```

- Curly braces `{}` mark a dictionary.
- Each entry is `"key": value`, separated by commas.
- You look things up **by name**, not by position: `user["username"]`.

Add or change entries:

```python
user["email"] = "api@example.com"      # add a new one
user["company"] = "ACME_TEST"          # change an existing one
print(user)
```

Looking up a key that doesn't exist crashes your program:

```python
print(user["phone"])        # KeyError: 'phone'
```

Use `.get()` when something might legitimately be missing:

```python
print(user.get("phone"))              # None  — no crash
print(user.get("phone", "unknown"))   # unknown — your own fallback
```

`None` is Python's word for "nothing here".

### Dictionaries inside dictionaries

This is exactly what SuccessFactors sends back, so get comfortable with it:

```python
response = {
    "d": {
        "results": [
            {"userId": "1001", "email": "a@example.com"},
            {"userId": "1002", "email": "b@example.com"}
        ]
    }
}

print(response["d"]["results"][0]["userId"])     # 1001
```

Read it **left to right**, one step at a time:
1. `response["d"]` → the inner dictionary
2. `["results"]` → the list inside it
3. `[0]` → the first item in that list
4. `["userId"]` → the value under that key

### Try it
Make a dictionary for a SuccessFactors config with keys `company_id`, `client_id`, and `token_url`. Print each value.

## 10. Repeating things — `for` loops

```python
modules = ["Employee Central", "Onboarding", "Compensation"]

for module in modules:
    print(module)
```

```text
Employee Central
Onboarding
Compensation
```

- `for X in Y:` — do the following, once for each item in `Y`. Each time round, `X` is the current item.
- `module` is a name **you** choose. `for thing in modules:` works identically.
- The **colon** at the end of the line is required.
- The **indentation** (4 spaces) is how Python knows which lines are inside the loop. This isn't style. It's syntax.

Indentation is Python's most distinctive feature:

```python
for module in modules:
    print(module)           # inside the loop — runs 3 times
print("Done")               # outside the loop — runs once
```

Get the indentation wrong and you get an `IndentationError`. VS Code handles it automatically when you press Enter after a colon.

Looping a dictionary:

```python
config = {"company_id": "ACME", "client_id": "key123"}

for key, value in config.items():
    print(f"{key} = {value}")
```

```text
company_id = ACME
client_id = key123
```

### Try it
Loop over a list of API endpoint names and print `f"Calling {name}"` for each.

## 11. Making decisions — `if`

```python
status_code = 200

if status_code == 200:
    print("Success!")
elif status_code == 401:
    print("Authentication failed")
else:
    print(f"Something else happened: {status_code}")
```

- `==` means "is equal to". **Two equals signs.** One (`=`) stores a value, two (`==`) compares. Mixing them up is a rite of passage.
- `elif` — "else if". Check this only if the previous test was false.
- `else` — if nothing above matched.
- Colon and indentation again, same rules as the loop.

Other comparisons:

```python
if count > 10:          # greater than
if count != 0:          # not equal to
if name in modules:     # is it in this list?
if not is_active:       # the opposite of
```

### Try it
Write a variable `token = ""` and an `if` that prints "No token" when it's empty. Hint: an empty string is treated as false, so `if not token:` works.

## 12. Functions — naming a job

A function bundles up some lines so you can run them whenever you want, with different inputs.

```python
def greet(name):
    print(f"Hello {name}")

greet("Kriba")
greet("Alex")
```

```text
Hello Kriba
Hello Alex
```

- `def` — "define a function".
- `greet` — the name you're giving it.
- `(name)` — the **parameter**: a placeholder for whatever gets passed in.
- Colon, then the indented body.
- `greet("Kriba")` — **calling** it. The function doesn't run until you call it.

Functions usually hand a value back, using `return`:

```python
def build_token_url(host):
    return f"https://{host}/oauth/token"

url = build_token_url("api.example.com")
print(url)
```

```text
https://api.example.com/oauth/token
```

`return` means "the answer is this, send it back to whoever called me". Everything after a `return` in that function is skipped.

Several inputs:

```python
def describe(user_id, company):
    return f"User {user_id} in company {company}"

print(describe("1001", "ACME"))
```

### Try it
Write a function `is_success(status_code)` that returns `True` when the code is 200 and `False` otherwise. Call it with 200 and with 401.

## 13. Using other people's code — `import`

Python comes with a huge amount of code already written. You bring it in with `import`:

```python
import datetime

now = datetime.datetime.now()
print(now)
```

```text
2026-10-07 14:32:11.482913
```

Or import just the piece you want:

```python
from datetime import datetime

now = datetime.now()
print(now)
```

Both work. The second saves typing.

Modules we'll use later: `base64`, `os`, `json`, `uuid`, `datetime`.

## 14. When things go wrong — errors

Your program will crash. Constantly. That's normal, and Python tells you exactly what happened.

```python
number = int("abc")
```

```text
Traceback (most recent call last):
  File "/home/you/projects/sf-oauth/test.py", line 1, in <module>
    number = int("abc")
ValueError: invalid literal for int() with base 10: 'abc'
```

**Read it from the bottom up.** The last line is the actual problem: `ValueError`, "abc" isn't a number. The line above tells you which file and which line number.

Sometimes you want to handle a failure rather than crash:

```python
try:
    number = int("abc")
    print(number)
except ValueError:
    print("That wasn't a number")
```

```text
That wasn't a number
```

- `try:` — attempt this.
- `except ValueError:` — if *that specific* kind of error happens, do this instead and keep going.

Errors you'll meet often:

| Error | Means |
|---|---|
| `SyntaxError` | Typo. A missing colon, bracket, or quote |
| `IndentationError` | Spacing is wrong |
| `NameError` | Using a variable you never created (often a typo in the name) |
| `TypeError` | Mixing types, like `"5" + 5` |
| `KeyError` | Asking a dictionary for a key it doesn't have |
| `ModuleNotFoundError` | Library not installed, or your virtual environment isn't active |

### Try it
Cause each of the first four deliberately. Read each message. Five minutes here saves hours later.

## 15. Checkpoint — commit your work

You now know enough Python to be dangerous. Save it in Git.

In VS Code's **Source Control** panel: you'll see your `.py` files listed. Hover over "Changes", click `+` to stage them all, type a message like `Python practice files`, click ✓.

Or in the terminal:

```bash
git init
git add -A
git commit -m "Python practice files"
```

If you haven't set up Git yet, [04a-git-quick-reference.md](04a-git-quick-reference.md) section 1 covers it.

---

# Part 3 — Real tools

## 16. Virtual environments

Different projects need different versions of libraries. A **virtual environment** gives this project its own private library folder so projects can't break each other.

```bash
cd ~/projects/sf-oauth
python3 -m venv .venv
```

- `-m venv` — run Python's built-in `venv` tool.
- `.venv` — the folder to create. The dot makes it hidden. VS Code looks for this name automatically.

Turn it on:

```bash
source .venv/bin/activate
```

Your prompt changes to show `(.venv)`. That means it's active.

- `source` — run this in the *current* terminal rather than a new one. Required here, because activation works by changing your current terminal's settings.

To turn it off: `deactivate`. **You must activate it again every time you open a new terminal.** Forgetting is the number one cause of `ModuleNotFoundError`.

In VS Code: press `Ctrl+Shift+P`, type "Python: Select Interpreter", and pick the one with `.venv` in the path. Now VS Code uses it too.

## 17. Installing a library

```bash
python3 -m pip install requests
```

`requests` is the standard library for making HTTP calls. Check it worked:

```bash
python3 -m pip list
```

Record what your project needs, so you (or another machine) can rebuild it:

```bash
python3 -m pip freeze > requirements.txt
```

- `>` — write the output into a file instead of showing it.

Later, on any machine: `python3 -m pip install -r requirements.txt` installs everything in one go.

## 18. Your first HTTP call

Create `http_test.py`:

```python
import requests

response = requests.get("https://httpbin.org/get", timeout=10)

print("Status code:", response.status_code)
print("Body:", response.text)
```

```bash
python3 http_test.py
```

```text
Status code: 200
Body: {
  "args": {},
  ...
}
```

You just made a real request over the internet from your own program.

- `requests.get(url)` — fetch something. GET means "give me this".
- `timeout=10` — give up after 10 seconds. **Always include this.** Without it, a server that never answers leaves your program hanging forever.
- `response.status_code` — the number the server returned.
- `response.text` — the body, as text.

### Status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request — you sent something malformed |
| 401 | Not authenticated — bad or missing credentials |
| 403 | Authenticated, but not allowed |
| 404 | Not found |
| 500 | The server broke |

Those first three will be your constant companions. **401 means your credentials are wrong. 403 means your credentials are fine but the user lacks permission.** Different problems, different fixes.

### GET vs POST

- **GET** — "give me this." Reading data.
- **POST** — "here's some information, process it." Sending data.

Getting a token is a POST. Reading employee records is a GET.

## 19. JSON

APIs send data as **JSON**, which looks almost exactly like a Python dictionary:

```json
{
  "access_token": "abc123",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

`requests` converts it for you:

```python
import requests

response = requests.get("https://httpbin.org/json", timeout=10)

data = response.json()          # JSON text -> Python dictionary

print(type(data))               # <class 'dict'>
print(data)
```

Once it's a dictionary, you already know how to read it:

```python
token = data["access_token"]
```

That's the whole trick. **JSON in, dictionary out.** Everything you learned in section 9 applies.

### Try it
Call `https://httpbin.org/get`, convert with `.json()`, and print just `data["url"]`.

## 20. Debugging in VS Code

Printing works, but the debugger is better and takes two minutes to learn.

1. Click just left of a line number. A **red dot** appears — that's a breakpoint.
2. Press `F5` to run. Choose "Python File" if asked.
3. Execution stops at the red dot.
4. The left panel shows **every variable and its current value**.
5. `F10` runs the next line. `F5` continues to the end.

Being able to freeze your program and look inside it is the single biggest jump in productivity you'll make. Use it whenever something isn't behaving.

---

# Part 4 — Config and keys

## 21. Keeping settings out of your code

Don't type your company ID and API key directly into your Python files. They'd get committed to Git and shared with anyone who sees the repository.

Install the helper:

```bash
python3 -m pip install python-dotenv
```

Create a file called `.env` (just a dot and "env"):

```text
SF_API_HOST=apisalesdemo2.successfactors.eu
SF_COMPANY_ID=your-company-id
SF_CLIENT_ID=your-api-key
SF_USER_ID=your-api-user
```

No quotes, no spaces around the `=`.

Create `.gitignore` so Git never picks it up:

```text
.env
.venv/
keys/
__pycache__/
*.pem
```

Now `config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()                       # read the .env file

API_HOST = os.environ["SF_API_HOST"]
COMPANY_ID = os.environ["SF_COMPANY_ID"]
CLIENT_ID = os.environ["SF_CLIENT_ID"]
USER_ID = os.environ["SF_USER_ID"]

TOKEN_URL = f"https://{API_HOST}/oauth/token"
ODATA_URL = f"https://{API_HOST}/odata/v2"
```

- `load_dotenv()` — reads `.env` and makes the values available.
- `os.environ["NAME"]` — fetch one of them. It's a dictionary, just like section 9.
- `API_HOST` in capitals — a convention meaning "this is a setting, don't change it while running".

Test it:

```python
# test_config.py
import config

print(config.TOKEN_URL)
print(config.COMPANY_ID)
```

- `import config` — bring in your *own* file. Same mechanism as `import requests`, except the file is yours. Note: no `.py` on the end.

### Try it
Run it. Then deliberately delete a line from `.env` and run again. You'll get a `KeyError` telling you exactly which setting is missing. That's useful behaviour, not a bug.

## 22. Generating a key pair

You need two matching files:

- A **private key** — stays on your machine, creates signatures. Secret.
- A **certificate** — contains the matching public key, uploaded to SuccessFactors so it can check your signatures. Not secret.

Think of it like a wax seal. The private key is the stamp, which only you have. The certificate is the pattern everyone can recognise. Anyone can verify the seal; only you can make it.

```bash
mkdir -p keys

openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out keys/private_key.pem

openssl req -new -x509 \
  -key keys/private_key.pem \
  -out keys/certificate.pem \
  -days 730 -sha256 \
  -subj "/CN=python-learning-app"

chmod 600 keys/private_key.pem
```

Command by command:

**First command** — create the private key.
- `openssl genpkey` — generate a key.
- `-algorithm RSA` — which maths to use. SuccessFactors needs RSA.
- `-pkeyopt rsa_keygen_bits:3072` — the key size. Bigger is stronger; 3072 is the current sensible default.
- `-out` — where to save it.

**Second command** — wrap the matching public key in a certificate.
- `openssl req -new -x509` — create a self-signed certificate. "Self-signed" means you vouch for it yourself, which is what SuccessFactors expects here.
- `-key` — use the private key you just made. These two must be a matching pair.
- `-days 730` — valid for two years. **Put the expiry in your calendar.** When it expires, your integration stops working.
- `-sha256` — the hashing method. SuccessFactors requires SHA-2; SHA-1 is rejected.
- `-subj "/CN=..."` — a name for the certificate. Skips a set of interactive prompts.

**Third command** — `chmod 600` makes the private key readable only by you. One line, worth doing.

Look at what you made:

```bash
openssl x509 -in keys/certificate.pem -noout -text
```

- `-noout` — don't print the raw certificate, just the readable summary.

## 23. Signing something, so you can see it work

Before touching SAML, prove the signing works on a simple message. If this works and the SAP call later fails, you know the problem isn't your key.

```bash
python3 -m pip install cryptography
```

`sign_test.py`:

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# 1. Read the private key file
with open("keys/private_key.pem", "rb") as f:
    key_data = f.read()

private_key = serialization.load_pem_private_key(key_data, password=None)

# 2. Sign a message
message = b"Hello SuccessFactors"

signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)

print("Signature length:", len(signature), "bytes")

# 3. Verify it with the public key
public_key = private_key.public_key()

try:
    public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
    print("Signature is valid")
except InvalidSignature:
    print("Signature is NOT valid")

# 4. Prove that changing the message breaks the signature
changed = b"Hello SuccessFactors!"

try:
    public_key.verify(signature, changed, padding.PKCS1v15(), hashes.SHA256())
    print("Changed message accepted — this should never happen")
except InvalidSignature:
    print("Changed message correctly rejected")
```

```text
Signature length: 384 bytes
Signature is valid
Changed message correctly rejected
```

Three new things:

**`with open(...) as f:`** — open a file, give it the name `f`, and close it automatically when the block ends. Always open files this way.

**`"rb"`** — read, binary. Not text.

**`b"Hello"`** — the `b` means **bytes**, not text. This is worth understanding properly, because it causes a lot of beginner confusion:

- `"Hello"` is text, for humans to read.
- `b"Hello"` is raw data, for computers.
- Cryptography only works on bytes, never on text.

Convert between them:

```python
text = "Hello"
data = text.encode("utf-8")      # text  -> bytes
back = data.decode("utf-8")      # bytes -> text
```

If you ever see `TypeError: a bytes-like object is required, not 'str'`, this is why. Add `.encode("utf-8")`.

The last part of the script matters conceptually. Changing one character makes the signature invalid. That's exactly the property SuccessFactors relies on to know your assertion wasn't tampered with.

---

# Part 5 — The SAP pieces

Now the Python you've learned gets pointed at SuccessFactors.

## 24. What a SAML assertion is

It's an XML document that says, in effect:

> "I am the client with API key X. I'm acting for user Y. This is for SuccessFactors. It's valid for the next 10 minutes. Here's my signature proving I wrote it."

SuccessFactors reads it, checks the signature against your uploaded certificate, and if everything matches, hands back an access token.

```xml
<saml2:Assertion ID="_abc123" IssueInstant="2026-10-07T14:00:00.000Z" Version="2.0">
  <saml2:Issuer>www.successfactors.com</saml2:Issuer>
  <saml2:Subject>
    <saml2:NameID>api_user</saml2:NameID>          <!-- which user -->
  </saml2:Subject>
  <saml2:Conditions NotBefore="..." NotOnOrAfter="...">
    <saml2:AudienceRestriction>
      <saml2:Audience>www.successfactors.com</saml2:Audience>   <!-- who it's for -->
    </saml2:AudienceRestriction>
  </saml2:Conditions>
  <saml2:AttributeStatement>
    <saml2:Attribute Name="api_key">
      <saml2:AttributeValue>your-api-key</saml2:AttributeValue>  <!-- which client -->
    </saml2:Attribute>
  </saml2:AttributeStatement>
</saml2:Assertion>
```

## 25. Building the XML in Python

```bash
python3 -m pip install lxml signxml
```

> [!WARNING]
> Don't build this XML by gluing strings together with f-strings. It looks like it should work and it won't. The signature is calculated over a precisely formatted version of the document, and only a proper XML library produces that format. Use `lxml`.

`saml.py`:

```python
import uuid
from datetime import datetime, timedelta, timezone
from lxml import etree

SAML_NS = "urn:oasis:names:tc:SAML:2.0:assertion"


def tag(name):
    """Build a full XML tag name in the SAML namespace."""
    return "{" + SAML_NS + "}" + name


def timestamp(when):
    """Format a time the way SAML wants it."""
    return when.strftime("%Y-%m-%dT%H:%M:%S.") + f"{when.microsecond // 1000:03d}Z"


def build_assertion(issuer, user_id, client_id, token_url, audience):
    now = datetime.now(timezone.utc)
    valid_from = now - timedelta(minutes=2)      # allow for clock differences
    valid_until = now + timedelta(minutes=10)

    assertion_id = "_" + uuid.uuid4().hex

    # The root element
    assertion = etree.Element(
        tag("Assertion"),
        nsmap={"saml2": SAML_NS},
        attrib={
            "ID": assertion_id,
            "IssueInstant": timestamp(now),
            "Version": "2.0",
        },
    )

    # Who issued it
    etree.SubElement(assertion, tag("Issuer")).text = issuer

    # Which user
    subject = etree.SubElement(assertion, tag("Subject"))
    name_id = etree.SubElement(subject, tag("NameID"))
    name_id.text = user_id

    confirmation = etree.SubElement(
        subject, tag("SubjectConfirmation"),
        Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"
    )
    etree.SubElement(
        confirmation, tag("SubjectConfirmationData"),
        NotOnOrAfter=timestamp(valid_until),
        Recipient=token_url,
    )

    # How long it's valid, and who it's for
    conditions = etree.SubElement(
        assertion, tag("Conditions"),
        NotBefore=timestamp(valid_from),
        NotOnOrAfter=timestamp(valid_until),
    )
    restriction = etree.SubElement(conditions, tag("AudienceRestriction"))
    etree.SubElement(restriction, tag("Audience")).text = audience

    # Required by the SAML format
    authn = etree.SubElement(
        assertion, tag("AuthnStatement"),
        AuthnInstant=timestamp(now),
        SessionIndex="_" + uuid.uuid4().hex,
    )
    context = etree.SubElement(authn, tag("AuthnContext"))
    etree.SubElement(context, tag("AuthnContextClassRef")).text = \
        "urn:oasis:names:tc:SAML:2.0:ac:classes:PreviousSession"

    # Which OAuth client
    attributes = etree.SubElement(assertion, tag("AttributeStatement"))
    api_key = etree.SubElement(attributes, tag("Attribute"), Name="api_key")
    etree.SubElement(api_key, tag("AttributeValue")).text = client_id

    return assertion
```

New things here:

- `"""..."""` just under a `def` — a **docstring**, describing what the function does. Optional but good habit.
- `etree.Element(...)` — create an XML element.
- `etree.SubElement(parent, ...)` — create an element inside another one.
- `.text = "value"` — set the text between the tags.
- `Method="..."` as an argument — becomes an XML attribute.
- `uuid.uuid4().hex` — a random unique ID. The `_` prefix is required, because XML IDs can't start with a digit.
- `\` at the end of a line — continue onto the next line. Only for very long lines.

**Why `valid_from` is two minutes in the past:** your clock and SAP's clock aren't perfectly synchronised. Without that cushion, a freshly created assertion can be rejected as "not valid yet". It's a small detail that causes maddening intermittent failures.

See what you built:

```python
if __name__ == "__main__":
    a = build_assertion("www.successfactors.com", "api_user", "key123",
                        "https://host/oauth/token", "www.successfactors.com")
    print(etree.tostring(a, pretty_print=True).decode("utf-8"))
```

- `if __name__ == "__main__":` — "only run this when I run *this* file directly, not when another file imports it." Put test code here.

## 26. Signing the XML

Add to `saml.py`:

```python
import base64
from signxml import XMLSigner


def sign_assertion(assertion, private_key_pem, certificate_pem):
    assertion_id = assertion.get("ID")

    signer = XMLSigner(
        method=signxml.methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    )

    signed = signer.sign(
        assertion,
        key=private_key_pem,
        cert=certificate_pem,
        reference_uri="#" + assertion_id,
    )

    # SAML wants the signature right after the Issuer element
    sig = signed.find("{http://www.w3.org/2000/09/xmldsig#}Signature")
    if sig is not None:
        signed.remove(sig)
        signed.insert(1, sig)

    return signed


def encode_assertion(signed_assertion):
    """Turn the signed XML into the Base64 text the OAuth request needs."""
    xml_bytes = etree.tostring(signed_assertion)
    return base64.b64encode(xml_bytes).decode("ascii")
```

- `signature_algorithm="rsa-sha256"` — RSA with SHA-256, matching the certificate you made.
- `reference_uri` — tells the verifier which part of the document the signature covers.
- The reorder at the end — the library puts the signature at the bottom; the SAML format requires it near the top. Moving it doesn't break the signature.

> [!NOTE]
> `signxml` has changed its options between versions. If you get an error about the algorithm arguments, run `python3 -m pip show signxml` and check that version's documentation. Pinning the version in `requirements.txt` avoids surprises.

### About Base64

```python
import base64

print(base64.b64encode(b"Hello"))        # b'SGVsbG8='
print(base64.b64decode(b"SGVsbG8="))     # b'Hello'
```

Base64 turns raw data into plain text so it can travel safely in an HTTP form field.

**Base64 is not encryption.** Anyone can decode it instantly. It hides nothing. The protection comes entirely from the signature, which is why section 23 mattered.

## 27. Getting the access token

`oauth.py`:

```python
import requests

GRANT_TYPE = "urn:ietf:params:oauth:grant-type:saml2-bearer"


def get_access_token(token_url, company_id, client_id, assertion_b64):
    payload = {
        "grant_type": GRANT_TYPE,
        "company_id": company_id,
        "client_id": client_id,
        "assertion": assertion_b64,
    }

    response = requests.post(token_url, data=payload, timeout=30)

    if response.status_code != 200:
        print("Token request failed:", response.status_code)
        print(response.text[:500])
        return None

    data = response.json()
    return data["access_token"]
```

- `requests.post(url, data=payload)` — send the dictionary as form data. `requests` handles all the escaping. Don't try to escape the assertion yourself; doing so breaks the signature.
- `response.text[:500]` — the first 500 characters of the error. `[:500]` is **slicing** — take a portion of something.
- `return None` on failure, so the caller can check.

SuccessFactors replies with:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "expires_in": 86399
}
```

- `expires_in` is in seconds, so that's about 24 hours.

## 28. Calling the OData API

`sf_api.py`:

```python
import requests


def get_users(odata_url, access_token, top=5):
    url = odata_url + "/User"

    headers = {
        "Authorization": "Bearer " + access_token,
        "Accept": "application/json",
    }

    params = {
        "$format": "json",
        "$top": top,
        "$select": "userId,username,email",
    }

    response = requests.get(url, headers=headers, params=params, timeout=60)

    if response.status_code != 200:
        print("API call failed:", response.status_code)
        print(response.text[:500])
        return []

    data = response.json()
    return data["d"]["results"]
```

- `headers` — extra information sent with the request. `Authorization: Bearer <token>` is how you present the token.
- `params` — the query string. `requests` builds and escapes it for you.
- `$top=5` — only 5 records, good for testing.
- `$select` — only these fields, rather than everything.
- `data["d"]["results"]` — SuccessFactors wraps results in a `d` object. This is the nested dictionary from section 9.

## 29. Putting it all together

`main.py`:

```python
import config
from saml import build_assertion, sign_assertion, encode_assertion
from oauth import get_access_token
from sf_api import get_users


def main():
    print("1. Reading key files...")
    with open("keys/private_key.pem", "rb") as f:
        private_key = f.read()
    with open("keys/certificate.pem", "rb") as f:
        certificate = f.read()

    print("2. Building the SAML assertion...")
    assertion = build_assertion(
        issuer="www.successfactors.com",
        user_id=config.USER_ID,
        client_id=config.CLIENT_ID,
        token_url=config.TOKEN_URL,
        audience="www.successfactors.com",
    )

    print("3. Signing it...")
    signed = sign_assertion(assertion, private_key, certificate)
    assertion_b64 = encode_assertion(signed)
    print("   Assertion is", len(assertion_b64), "characters long")

    print("4. Requesting an access token...")
    token = get_access_token(
        config.TOKEN_URL,
        config.COMPANY_ID,
        config.CLIENT_ID,
        assertion_b64,
    )

    if token is None:
        print("Could not get a token. Stopping.")
        return

    print("   Got a token.")

    print("5. Calling the OData API...")
    users = get_users(config.ODATA_URL, token)

    print(f"   Got {len(users)} users:")
    for user in users:
        print("   -", user.get("userId"), user.get("email"))


main()
```

Run it:

```bash
source .venv/bin/activate
python3 main.py
```

The numbered prints mean that when something fails, you immediately know which of the five steps broke.

- `from saml import build_assertion, ...` — import specific functions from your own file.
- `return` with nothing after it — leave the function early.

## 30. What you need from SuccessFactors

Someone with admin access must set this up:

1. **Admin Center → API Center → OAuth Configuration for OData → Register Client Application**
2. Give it a name, any URL, and paste in the contents of your `keys/certificate.pem` (including the `BEGIN` and `END` lines).
3. Save. SuccessFactors generates an **API key** — that goes in your `.env` as `SF_CLIENT_ID`.
4. You also need an **API user** that exists and is active, with permission to read the entities you're querying.
5. Check the correct **API server hostname** for your data centre. Using the wrong one looks like a credential error but isn't.

> [!TIP]
> Use a test or demo instance while learning, not a production tenant.

---

# Part 6 — When it doesn't work

## 31. Troubleshooting

| What you see | Likely cause | What to check |
|---|---|---|
| `ModuleNotFoundError` | Virtual environment isn't active | `source .venv/bin/activate` |
| `IndentationError` | Spacing is wrong | 4 spaces, consistently |
| `KeyError: 'SF_COMPANY_ID'` | Missing line in `.env` | Open `.env` and check |
| `TypeError: a bytes-like object is required` | Text where bytes belong | Add `.encode("utf-8")` |
| `FileNotFoundError: keys/private_key.pem` | Wrong folder | `pwd` to see where you are |
| HTTP 401 on the token call | Assertion rejected | See below |
| HTTP 401 on the OData call | Token expired or wrong | Get a fresh token |
| HTTP 403 on the OData call | Token is fine, user lacks permission | SF role permissions |
| `Invalid user` | Wrong user ID in `.env` | Confirm with your SF admin |
| `assertion has expired` | Clock difference | Your machine's time; `timedatectl` |

### If the token request fails

Work through in this order:

1. **Does your signing test still pass?** Run `sign_test.py`. If yes, the key is fine.
2. **Does the certificate in SuccessFactors match your file?** Check the fingerprint:
   ```bash
   openssl x509 -in keys/certificate.pem -noout -fingerprint -sha256
   ```
3. **Is the API key in `.env` exactly what SF generated?** It appears in two places (the form field *and* inside the assertion), and both must match.
4. **Is the `Issuer` value right?** This is the most common failure. Examples use `www.successfactors.com`, but your tenant may expect something else. Ask whoever configured the OAuth client.
5. **Is your clock correct?** `timedatectl` — if it says not synchronised, fix that first.

### Look at what you actually sent

```python
print(etree.tostring(signed, pretty_print=True).decode("utf-8"))
```

Compare it element by element against the example in section 24.

## 32. Using Git with this project

In VS Code's Source Control panel, after each working step:

1. Check the diff by clicking a changed file.
2. Stage with `+`.
3. Write a message: "Add SAML assertion builder".
4. Click ✓.

Commit at every point where something newly works. That way when you break something, you can get back to working code:

```bash
git log --oneline          # find the commit where it worked
git restore .              # throw away uncommitted mess
```

Make sure your `.gitignore` has `.env` and `keys/` **before your first commit**. Once something is committed it stays in the history even if you delete it later.

---

## What you've learned

**Python:** variables, types, strings and f-strings, lists, dictionaries, nested dictionaries, loops, conditions, functions, imports, errors and `try`/`except`, files, bytes vs text, virtual environments, pip.

**Tools:** VS Code, its debugger, its Git panel, the terminal, OpenSSL basics.

**Concepts:** HTTP and status codes, GET vs POST, JSON, public/private keys, digital signatures, Base64, XML, SAML assertions, OAuth tokens, OData.

**And the SAP connection:** when you configure an OAuth2 SAML Bearer credential in Cloud Integration, it's doing exactly these five steps for you. The keystore holds the key, the credential fields set the Issuer, Audience, and api_key, and the adapter attaches the Bearer token. You now know what's behind each field.

## Where to go next

1. **Run it, break it, fix it.** Change a value in `.env` and watch which error appears. That mapping from symptom to cause is the actual skill.
2. **Add a function** that queries a different entity, like `PerPerson`.
3. **Handle more than 5 records.** SuccessFactors pages results — look for `__next` in the response.
4. **Read the professional version**, [03-python-sf-oauth-saml-bearer.md](03-python-sf-oauth-saml-bearer.md). Same program, written properly: type hints, classes, logging, token caching, retries. Seeing both versions is where the real learning happens.
5. **Python basics you haven't met yet:** `while` loops, list comprehensions, classes, `pathlib`, testing with `pytest`.

## References

- [Official Python tutorial](https://docs.python.org/3/tutorial/) — dense but correct
- [Real Python](https://realpython.com/) — good beginner articles
- [requests documentation](https://requests.readthedocs.io/en/latest/)
- [VS Code Python tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [SAP SuccessFactors API Reference Guide (OData V2)](https://help.sap.com/docs/successfactors-platform/sap-successfactors-api-reference-guide-odata-v2)
- [SAP SuccessFactors HCM documentation](https://help.sap.com/docs/successfactors-hcm?locale=en-US)
- [SAP Developer Tutorials](https://developers.sap.com)
