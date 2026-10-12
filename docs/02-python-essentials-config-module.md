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
# Python + SAP — Step 2: Python Essentials by Building `config.py`

Goal: learn the Python you need — variables, strings, bytes, dictionaries, functions, modules, exceptions, type hints — by writing the real configuration module the rest of this build depends on. Not a toy. The `config.py` produced here is imported by the OAuth client in Phase C, the extractor in Phase D, and the database loader in Phase F without modification.

All work happens in **VS Code**. Every file is created through the editor, every program runs through the Run or Debug button, and every shell command goes into VS Code's integrated terminal. Section 1 sets up the workbench, including the debugger — which is the single most useful tool for learning a language, because it lets you stop a program mid-execution and look at the actual values rather than guessing from printed output.

The concept block for this document is the **process environment**: what an environment variable actually is at the operating system level, how it is inherited, why it is the correct place for secrets, and where that stops being true.

Prerequisites from [01-python-environment-on-fedora](01-python-environment-on-fedora.md) are condensed into section 0. That document explains *why* each step is what it is; read it when something breaks.

## Architecture

```
   ~/.bashrc  /  systemd unit  /  .env file
                      │
                      │  exported into the process environment
                      ▼
          ┌─────────────────────────────┐
          │  your Python process        │
          │                             │
          │   os.environ  ──────────┐   │
          │                         │   │
          │   config.py ◄───────────┘   │
          │      │                      │
          │      │ validates, converts, │
          │      │ fails loudly         │
          │      ▼                      │
          │   Config object             │
          │      │                      │
          │      ├──► oauth.py          │
          │      ├──► extract.py        │
          │      └──► db.py             │
          └─────────────────────────────┘

   secrets never appear in source, never appear in git,
   never appear in a log line
```

## 0. Prerequisites (condensed from document 01)

Open VS Code and use **Terminal → New Terminal** (`Ctrl+` `` ` ``) for everything in this section. The integrated terminal is an ordinary shell — there is nothing special about it except that it opens in your project directory and automatically activates the virtual environment once section 1.3 is done.

```bash
sudo dnf install python3-pip python3-devel gcc libxml2-devel libxslt-devel libpq-devel
```
Development headers and a C compiler. `lxml` (Phase E) and `psycopg` (Phase F) are Python wrappers around C libraries and may need to compile during installation. Installing these now avoids an unrelated detour later.

```bash
mkdir -p ~/projects/sf-integration/{src,keys,docs,tests,scratch}
cd ~/projects/sf-integration
chmod 700 keys
```
- `{src,keys,docs,tests,scratch}` — **brace expansion**, a shell feature. The shell expands this into five separate arguments before `mkdir` runs.
- `scratch/` — a throwaway directory for the learning exercises in sections 2 to 8. Separate from `src/`, which holds real project code.
- `chmod 700 keys` — owner-only access. Private keys land here in Phase B.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests python-dotenv
```
- `-m venv` — create an isolated package directory for this project.
- `source` — run the activation script **in the current shell** so it can modify your `PATH`. A normal invocation would run in a subshell and the changes would vanish.
- `python-dotenv` — reads a `.env` file into the environment; used in section 9.

```bash
git init
```

Now open the project properly in VS Code: **File → Open Folder** → `~/projects/sf-integration`. Everything from here on assumes this folder is your workspace root.

Create `.gitignore` through the editor — right-click in the Explorer pane, **New File**, name it `.gitignore`, and paste:

```gitignore
.venv/
__pycache__/
*.pyc
.env
keys/
*.key
*.pem
scratch/
```

Do not skip this. A private key committed to Git survives in history and in every clone; deleting it later does not help, and the only real fix is rotating the key.

```bash
git add .gitignore && git commit -m "Initial structure"
```

## 1. VS Code as your Python workbench

Five things to set up once. The debugger in 1.5 is the one that changes how you learn.

### 1.1 Extensions

Open the Extensions pane (`Ctrl+Shift+X`) and install:

- **Python** (Microsoft) — interpreter discovery, the Run button, debugging, test integration.
- **Pylance** (Microsoft) — the language server: completion, hover documentation, inline type errors.

Nothing else is required. Resist the urge to install twenty extensions; the two above plus the editor's built-in features cover this entire build.

### 1.2 The panes you will live in

```
┌──────────┬───────────────────────────────┬──────────────┐
│          │                               │              │
│ Explorer │        Editor                 │   Outline    │
│  (files) │                               │              │
│          │                               │              │
├──────────┴───────────────────────────────┴──────────────┤
│  Terminal │ Problems │ Debug Console │ Output           │
└──────────────────────────────────────────────────────────┘
```

- **Explorer** (`Ctrl+Shift+E`) — your files. Right-click → New File is how every file in this document gets created.
- **Terminal** (`` Ctrl+` ``) — the integrated shell, for `dnf`, `git`, and the Linux inspection commands in section 9.
- **Problems** (`Ctrl+Shift+M`) — where Pylance reports type errors and unresolved imports *before* you run anything.
- **Debug Console** — a Python prompt attached to your paused program. Section 1.5.
- **Command Palette** (`Ctrl+Shift+P`) — everything VS Code can do, searchable by name. When this document says "run the command X", it means type `Ctrl+Shift+P` then X.

### 1.3 Select the interpreter

The single most important configuration step.

```
Ctrl+Shift+P  →  Python: Select Interpreter  →  ./.venv/bin/python
```

Without this, VS Code uses the system Python, Pylance reports `requests` as unresolved with a red squiggle, and the debugger runs against the wrong packages. The symptom is import errors in the editor on code that works fine in the terminal.

Confirm it: the status bar at the bottom should read something like `Python 3.12.7 ('.venv': venv)`.

### 1.4 Workspace settings

Create `.vscode/settings.json` — Explorer → New Folder `.vscode`, then New File `settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.inlayHints.functionReturnTypes": true,
  "python.analysis.inlayHints.variableTypes": true,
  "editor.formatOnSave": false,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

- `python.defaultInterpreterPath` — which interpreter to use. `${workspaceFolder}` is a VS Code variable resolving to the project root, keeping the setting portable.
- `python.terminal.activateEnvironment` — every new integrated terminal runs `source .venv/bin/activate` automatically. You will never again install a package into the wrong environment by accident.
- `typeCheckingMode: "basic"` — Pylance checks type hints and flags mismatches. Section 8 explains what these are; having the editor enforce them from the start is how they become useful rather than decorative. `"strict"` is available later, once you're comfortable.
- `inlayHints` — Pylance displays *inferred* types inline, greyed out, next to variables and return values. For someone learning the language this is genuinely valuable: you see what Python thinks each expression is, without adding a single `print()`.
- `files.trimTrailingWhitespace` — trailing spaces in a configuration value cause authentication failures with error messages that tell you nothing. Section 3.2 returns to this.

Reload the window so the settings take effect: `Ctrl+Shift+P` → **Developer: Reload Window**.

### 1.5 Running and debugging

Two ways to run the file currently open in the editor:

- **Run** — the ▷ button at the top right, or `Ctrl+F5`. Executes the file in the integrated terminal. Output appears there.
- **Debug** — `F5`, or the Run and Debug pane (`Ctrl+Shift+D`). Executes with the debugger attached.

Debugging is not only for broken code. It is the fastest way to understand what a program is actually doing.

**Set a breakpoint** by clicking in the narrow margin to the left of a line number. A red dot appears. Press `F5`, and execution stops *before* that line runs. You now have:

- **Variables pane** — every name currently in scope with its live value, expandable for dictionaries and objects.
- **Debug Console** — a Python prompt running inside the paused program. Type any expression and see its value in the current context.
- **Watch pane** — expressions re-evaluated every time execution stops.
- **Call Stack** — which function called which to get here.

The stepping controls:

| Key | Action | Meaning |
|---|---|---|
| `F5` | Continue | Run until the next breakpoint |
| `F10` | Step Over | Execute this line; don't descend into function calls |
| `F11` | Step Into | Descend into the function being called on this line |
| `Shift+F11` | Step Out | Finish the current function and stop at the caller |
| `Shift+F5` | Stop | Terminate |

Throughout sections 2 to 8, where a concept is subtle, this document tells you where to put a breakpoint and what to inspect. That beats `print()` every time — you see *everything* in scope, not just what you remembered to print.

### 1.6 The scratch file workflow

The learning exercises use `scratch/`. The workflow for each:

1. Explorer → right-click `scratch` → **New File** → name it, e.g. `01_names.py`
2. Type or paste the code
3. `Ctrl+F5` to run, or `F5` with a breakpoint set to inspect

`scratch/` is in `.gitignore` — these files are for understanding, not for keeping.

One VS Code behaviour worth knowing: by default it runs the file in the *workspace root*, not the file's directory. So `scratch/01_names.py` runs with the working directory set to `~/projects/sf-integration`. That matters in section 10, where `config.py` deliberately avoids depending on the working directory at all.

## 2. Variables are names bound to objects

Create `scratch/01_names.py`:

```python
a = "ACMECORP"
b = a

print(id(a), id(b))
print(a is b)
print(a == b)
```

- `id()` — the object's identity, in CPython its memory address.
- `is` — identity comparison: are these two names bound to the *same object*?
- `==` — value comparison: do these two objects have equal content?

Run it (`Ctrl+F5`). Both `id` values are identical.

In many languages `a = "ACMECORP"` means "a box called `a` now holds a string." In Python it means something different. There are **objects** and there are **names**. The string is an object somewhere in memory; `a` is a label bound to it. `b = a` did not copy anything — it attached a second label to the same object.

### 2.1 Mutable and immutable

Create `scratch/02_mutability.py`:

```python
settings = {"company": "ACMECORP"}
alias = settings

alias["company"] = "CHANGED"

print(settings)
```

**Put a breakpoint on the `alias["company"] = "CHANGED"` line** and press `F5`. In the Variables pane, expand both `settings` and `alias` — both show `company: 'ACMECORP'`. Press `F10` to step over that one line, and watch *both* update to `'CHANGED'`.

There was only ever one dictionary.

Strings, integers and tuples are **immutable** — operations produce new objects rather than altering existing ones. Lists, dictionaries and sets are **mutable**. A function that receives a dictionary can modify the caller's data; a function that receives a string cannot.

**Why this appears in a configuration document:** the `Config` object built in section 10 is deliberately made immutable. Configuration that any module can quietly mutate is configuration you cannot reason about when the extractor behaves differently on its third run than its first.

### 2.2 Naming conventions

From PEP 8, Python's style guide:

```python
company_id = "ACMECORP"          # snake_case for variables and functions
TOKEN_TIMEOUT_SECONDS = 30       # UPPER_CASE for module-level constants
class OAuthClient:               # PascalCase for classes
    ...
def request_access_token():      # snake_case for functions
    ...
_internal_cache = {}             # leading underscore: "private by convention"
```

The leading underscore is not enforced by the language. It is a signal to other readers — and Pylance will deprioritise such names in its completion suggestions, which is a useful nudge.

## 3. Strings, and the bytes/str distinction

Single and double quotes are identical in Python. Pick one and be consistent; use the other when the string contains a quote.

### 3.1 f-strings

Create `scratch/03_strings.py`:

```python
host = "api.example.com"
count = 1234567
secret = "supersecret"

print(f"https://{host}/oauth/token")
print(f"{host=}")
print(f"{count:,}")
print(f"{secret[:4]}...")
```

- The `f` prefix makes it an **f-string**: anything in `{}` is evaluated as a Python expression and its result substituted.
- `{host=}` — the `=` suffix prints both the expression and its value. Excellent for quick debugging.
- `{count:,}` — a **format specification** after the colon; here, thousands separators.
- `secret[:4]` — **slicing**: characters from the start up to (not including) index 4. Used in section 10 to log a truncated credential rather than a whole one.

f-strings are the primary tool for building URLs, XML fragments and log messages throughout this build.

**One rule to internalise now:** never put an externally-sourced value into SQL with an f-string. That is SQL injection, and Phase F covers the correct approach. f-strings for URLs and logs, parameterised queries for SQL.

### 3.2 String methods, and `repr`

Add to `scratch/03_strings.py`:

```python
raw = "  ACMECORP  \n"

print(raw.strip())
print(repr(raw.strip()))
print(repr(raw))

print("api.example.com".startswith("https://"))
print("a,b,c".split(","))
print("-".join(["2026", "10", "12"]))
```

- `.strip()` — remove leading and trailing whitespace. Returns a *new* string; the original is unchanged, because strings are immutable.
- `repr()` — the unambiguous representation, showing quotes and escape sequences.

Compare the second and third lines of output. `print(raw)` and `print(repr(raw))` look entirely different, and `repr` is what you want when checking whether a stray newline is present.

This is not academic. Values read from `.env` files and shell exports frequently carry trailing whitespace, and a company ID with an invisible trailing space produces a SuccessFactors authentication failure whose error message tells you nothing useful. `config.py` calls `.strip()` on every value for exactly this reason.

**In the debugger:** set a breakpoint after `raw` is assigned and look at the Variables pane. VS Code shows the `repr` form, so `'  ACMECORP  \n'` with the whitespace visible. Another reason the debugger beats `print()`.

### 3.3 `str` versus `bytes`

This distinction causes more confusion than any other single thing in Python, and Phases B and C are built on it.

```
str    — a sequence of Unicode characters.   "Hello"
bytes  — a sequence of 8-bit integers.       b"Hello"
```

Create `scratch/04_bytes.py`:

```python
text = "Hello"
data = text.encode("utf-8")
back = data.decode("utf-8")

print(type(text), type(data))
print(text)
print(data)
print(text == back)

# This fails — uncomment to see the error
# print(text + data)
```

- `.encode()` — convert text to bytes using a character encoding. UTF-8 is the correct default in essentially all modern contexts.
- `.decode()` — the reverse.

Note `b'Hello'` in the output — the `b` prefix marks a bytes literal. Uncomment the last line and run again: `TypeError: can only concatenate str (not "bytes") to str`. Pylance will also flag it in the Problems pane *before* you run, with a red squiggle on the line. That is the type checking from section 1.4 earning its place.

**Why this will matter.** Cryptography operates on bytes, never on text. When you sign the SAML assertion in Phase C, the library requires bytes; passing a `str` raises `TypeError`. Base64 encoding takes bytes and produces bytes. HTTP bodies are bytes on the wire. The mental model:

```
    your XML as text (str)
            │  .encode("utf-8")
            ▼
         bytes  ──► hash ──► sign ──► base64 ──► bytes
                                                  │ .decode("ascii")
                                                  ▼
                              text, to put in the HTTP form field
```

Every `TypeError: a bytes-like object is required` you hit in Phase C is a missing `.encode()` or `.decode()` at one of those four boundaries.

## 4. Dictionaries

The central data structure of this build. JSON responses from SuccessFactors become dictionaries. HTTP headers are dictionaries. OAuth form parameters are dictionaries.

Create `scratch/05_dicts.py`:

```python
oauth_request = {
    "company_id": "ACMECORP",
    "client_id": "ABCDEF123456",
    "grant_type": "urn:ietf:params:oauth:grant-type:saml2-bearer",
}

print(oauth_request["company_id"])
print(oauth_request.get("assertion"))
print(oauth_request.get("assertion", "not yet built"))
print("client_id" in oauth_request)

for key, value in oauth_request.items():
    print(f"{key} = {value}")
```

A dictionary maps **keys** to **values**. Keys must be immutable (strings, nearly always). Insertion order is preserved as of Python 3.7.

- `[...]` — direct access. Raises `KeyError` if the key is absent.
- `.get(key)` — returns `None` if absent.
- `.get(key, default)` — returns the default if absent.
- `in` — membership test.
- `.items()` — yields `(key, value)` pairs, unpacked into two loop variables. `.keys()` and `.values()` yield one or the other.

Note the indentation on the `for` loop: Python uses it as syntax, not decoration. Four spaces per level, never tabs. VS Code's Python extension handles this automatically — and if you paste code with mixed indentation, the Problems pane tells you immediately.

**Which access form to use is a design decision, not a style preference.** Use `[...]` when a missing key means the program is broken and should stop. Use `.get()` with a default when absence is legitimate. In `config.py`, a missing `SF_CLIENT_ID` means stop — there is no sensible default, and continuing produces a confusing failure three layers down instead of a clear one at startup.

### 4.1 Nested structures

SuccessFactors OData responses arrive nested. Add to `scratch/05_dicts.py`:

```python
response = {
    "d": {
        "results": [
            {"userId": "12345", "firstName": "Alex"},
            {"userId": "67890", "firstName": "Sam"},
        ]
    }
}

print(response["d"]["results"][0]["userId"])

for record in response["d"]["results"]:
    print(record["firstName"])
```

Each `[...]` steps down one level; `[0]` indexes into the list.

**Put a breakpoint on the first `print`** and expand `response` in the Variables pane. You get a tree view of the whole structure — `d` → `results` → `0` → `userId`. When you're parsing a real 40-field SuccessFactors response in Phase D, this tree is how you find the field you need without printing the whole payload.

This exact shape is what Phase D parses. A missing intermediate key produces `KeyError: 'd'`, which once you recognise it tells you immediately that the response was an error payload rather than a result set.

## 5. Functions

Create `scratch/06_functions.py`:

```python
def build_token_url(hostname: str) -> str:
    """Return the OAuth token endpoint for a SuccessFactors host."""
    return f"https://{hostname}/oauth/token"


print(build_token_url("apisalesdemo8.successfactors.com"))
```

- `def` — define a function.
- `hostname: str` — a **type hint**: this parameter is expected to be a string. Section 8 covers these.
- `-> str` — a type hint for the return value.
- The triple-quoted string — a **docstring**. Hover over `build_token_url` anywhere it's used and VS Code shows it. That is Pylance reading the docstring, and it is why writing them pays off immediately rather than eventually.
- `return` — produce a value to the caller. A function with no `return` returns `None`.

Two blank lines between top-level definitions is the PEP 8 convention.

### 5.1 Parameters, defaults and keyword arguments

```python
def describe_timeout(seconds: float = 30.0, retries: int = 3) -> str:
    return f"timeout={seconds}s retries={retries}"


print(describe_timeout())
print(describe_timeout(60.0))
print(describe_timeout(retries=5))
print(describe_timeout(seconds=10.0, retries=1))
```

Keyword arguments are worth the extra typing when a function takes more than two parameters. `connect(host, 30, True, False)` is unreadable; `connect(host, timeout=30, verify=True, retry=False)` is not.

**Use VS Code's signature help:** type `describe_timeout(` and a tooltip appears showing the parameters, their types and their defaults, with the current one highlighted. Press `Ctrl+Shift+Space` to bring it back if it disappears.

### 5.2 The mutable default trap

```python
def add_header(headers: dict = {}):      # WRONG
    headers["X-Custom"] = "value"
    return headers


print(add_header())
print(add_header())
print(add_header())
```

Run it. The dictionary grows across calls — or rather, it is the *same* dictionary every time, because the default value is evaluated **once**, when the function is defined, not on each call.

The correct form:

```python
def add_header(headers: dict | None = None) -> dict:
    if headers is None:
        headers = {}
    headers["X-Custom"] = "value"
    return headers
```

Never use a mutable default. This follows directly from section 2.1.

## 6. Modules and imports

A **module** is simply a `.py` file. A file named `config.py` is importable as `config`.

```python
import os
from pathlib import Path
from dataclasses import dataclass
```

- `import os` — load the module; access members as `os.environ`.
- `from pathlib import Path` — load the module and bind one name from it directly, so you write `Path(...)` rather than `pathlib.Path(...)`.

Avoid `from module import *`. It pulls every public name into your namespace, and when two modules define the same name you get a bug that takes an hour to find.

**Two VS Code features that make imports painless:**

- Start typing a name Pylance recognises — `Path`, say — and the completion list offers it with "Auto-import from pathlib" attached. Accept it and the import statement is added at the top of the file automatically.
- `Ctrl+Click` (or `F12`) on any imported name jumps to its definition — including into the standard library source. Reading how `pathlib` is actually implemented is a genuinely good way to learn idiomatic Python.

### 6.1 Import ordering

Conventional grouping, blank line between groups:

```python
import os                        # 1. standard library
from pathlib import Path

import requests                  # 2. third-party
from dotenv import load_dotenv

from config import load_config   # 3. your own modules
```

### 6.2 `__name__` and the main guard

Every module has a `__name__` attribute. When a file is run directly it is `"__main__"`; when imported it is the module's name.

```python
if __name__ == "__main__":
    main()
```

Code under that guard runs when you execute the file, and does not run when another module imports it. Without it, importing `config.py` would execute its demonstration code as a side effect — exactly the kind of thing that makes a program behave differently under test than in production.

You will see this at the bottom of `config.py` in section 10, and section 10.4 demonstrates it working.

## 7. Exceptions

Create `scratch/07_exceptions.py`:

```python
cfg = {"company_id": "ACMECORP"}

try:
    value = cfg["client_id"]
except KeyError as exc:
    print(f"Missing key: {exc}")
```

- `try:` — attempt this.
- `except KeyError as exc:` — if a `KeyError` occurs, bind the exception object to `exc` and run this block.
- Any other exception type propagates upward, unhandled here.

### 7.1 Raising your own

```python
class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def check(value: str | None) -> str:
    if not value:
        raise ConfigError("value is empty")
    return value


check(None)
```

- `class ConfigError(Exception)` — define a new exception type inheriting from the built-in `Exception`. The docstring is the entire body; no other code is needed.
- `raise` — signal the error.

Run this one with `F5` rather than `Ctrl+F5`. When the exception is raised, **the debugger stops at the raising line** and shows you the full state at the moment of failure — every local variable, the whole call stack. Compare that to reading a traceback in the terminal after the program has already exited. For diagnosing anything non-obvious, this is the difference.

By default VS Code breaks only on *uncaught* exceptions. In the Run and Debug pane there is a **Breakpoints** section with checkboxes for "Raised Exceptions" and "Uncaught Exceptions" — enabling the first stops on every raise, including ones inside `try` blocks. Useful when something is being swallowed and you need to find out where.

A custom exception type lets callers catch *your* configuration problems specifically, rather than catching everything and hiding real bugs.

### 7.2 Catch narrowly

```python
try:
    token = request_token()
except Exception:          # too broad — hides typos, interrupts, everything
    token = None
```

A bare `except Exception` catches programming errors as readily as expected failures, and `token = None` then carries the problem silently into the next function. Catch the specific types you can actually handle:

```python
try:
    token = request_token()
except requests.Timeout:
    # a timeout is expected occasionally — retry
    ...
except requests.HTTPError as exc:
    # a 401 means the credentials are wrong; no retry will fix that
    raise ConfigError("Authentication rejected — check client ID") from exc
```

- `raise ... from exc` — **exception chaining**. The traceback shows both your error and the original cause. Without `from`, you discard the underlying detail, which is precisely what you need at 2am.

### 7.3 Fail fast, and fail at startup

The design principle for `config.py`: validate everything the moment the program starts, and raise immediately on anything missing. The alternative — discovering a missing private key path twenty minutes into an extraction run — is strictly worse. The traceback at startup names the exact variable; the failure mid-run names a file operation in a module you weren't thinking about.

Same reasoning as validating externalised parameters at iFlow deployment rather than at first message.

## 8. Type hints

```python
def get_required(name: str) -> str:
    ...
```

Python does not enforce these at runtime. Passing an integer where `str` is annotated raises nothing. So what are they for?

1. **Pylance** flags mismatches in the Problems pane as you type — with `typeCheckingMode: "basic"` from section 1.4, you get this for free.
2. **Readers**, including you in six months, learn the contract without reading the body.
3. **`mypy`** can check them across the whole codebase as a separate CI step later.

Create `scratch/08_types.py`:

```python
from pathlib import Path

name: str = "ACMECORP"
count: int = 10
enabled: bool = True
timeout: float = 30.0
path: Path = Path("keys/private_key.pem")
items: list[str] = ["a", "b"]
headers: dict[str, str] = {"Accept": "application/json"}
maybe: str | None = None

# Pylance flags this before you run it:
count = "not a number"
```

The red squiggle on the last line, and its entry in the Problems pane, is the type checker working. Hover over it for the explanation.

The `|` syntax for "this or that" requires Python 3.10+; Fedora's Python is well past that.

**Inlay hints in action:** the settings from section 1.4 make Pylance display inferred types greyed out inline. Write `result = build_token_url("x")` with no annotation and you'll see `: str` appear after `result` without typing it. That constant feedback about what Python thinks each expression is, is one of the better ways to build intuition.

### 8.1 `pathlib.Path`

Create `scratch/09_paths.py`:

```python
from pathlib import Path

p = Path("~/projects/sf-integration/keys/private_key.pem").expanduser()

print(p)
print(p.parent)
print(p.name)
print(p.suffix)
print(p.exists())
print(p.is_absolute())
```

- `Path(...)` — construct a path object. Preferred over plain strings everywhere.
- `.expanduser()` — expand a leading `~` to the home directory. The shell does this automatically; **Python does not**, which is a common source of "file not found" when a path from a `.env` file starts with `~`.
- `.parent`, `.name`, `.suffix` — path components without string manipulation.
- `.exists()` — check presence on disk.

`config.py` uses `Path` for the private key location and validates existence at startup.

## 9. The process environment — the concept block

Configuration has to come from outside the source code. On Linux that is primarily the process environment, so it's worth understanding what that actually is. This section uses the integrated terminal (`` Ctrl+` ``).

### 9.1 What an environment variable is

Every process on Linux carries a block of `KEY=VALUE` strings in its memory, set up by whatever started it. It is not a global registry, not a file, and not shared between processes.

```bash
printenv | head -10
```
- `printenv` — print the environment of the current process.

Look at the raw block:

```bash
cat /proc/$$/environ | tr '\0' '\n' | head -10
```
- `/proc/` — a virtual filesystem exposing kernel data as files. Nothing here exists on disk.
- `$$` — a shell variable holding the current shell's process ID.
- `environ` — the raw environment block for that process.
- `tr '\0' '\n'` — translate NUL bytes to newlines. The variables are NUL-separated in memory, so without this you get one unreadable line.

You are reading the actual memory structure the kernel set up when your shell started.

### 9.2 Inheritance, and `export`

A child process receives a **copy** of its parent's environment at creation. Changes afterwards propagate in neither direction.

```bash
MY_VAR="hello"
python -c "import os; print(os.environ.get('MY_VAR'))"
```

Prints `None`. The variable exists as a shell variable, but was never placed in the environment block that `python` inherited.

```bash
export MY_VAR="hello"
python -c "import os; print(os.environ.get('MY_VAR'))"
```
- `export` — mark a shell variable for inclusion in the environment of child processes.

Now prints `hello`.

One-way, and copied:

```bash
export PARENT_VALUE="original"
bash -c 'export PARENT_VALUE="changed"; echo "child sees: $PARENT_VALUE"'
echo "parent still: $PARENT_VALUE"
```

The child's change is invisible to the parent. This is why a script cannot set environment variables for your shell unless you `source` it — the same mechanism behind `source .venv/bin/activate` in section 0, and behind VS Code's `activateEnvironment` setting.

### 9.3 Visibility, and the limits of this approach

```bash
export SF_FAKE_SECRET="pretend-secret"
ps eww -p $$ | tr ' ' '\n' | grep SF_FAKE
unset SF_FAKE_SECRET
```
- `ps` — report on processes.
- `e` — show the environment of each process.
- `ww` — unlimited output width, so long values aren't truncated.
- `-p $$` — this shell.

The value is visible. Environment variables are readable by the process owner and by root, and they leak into crash dumps, into child processes you didn't intend, and into CI logs that dump the environment for debugging.

**The honest position:** environment variables are much better than hardcoded secrets and are the standard mechanism, but they are not a secret *store*. For this lab they are correct. For a production version of this integration, the escalation path is a secrets manager — SAP BTP Credential Store, HashiCorp Vault, or `systemd` credentials — which deliver the secret to the process without it sitting in the environment block. Phase G revisits this.

### 9.4 `.env` files

Typing `export` for seven variables before every run is tedious and error-prone. The convention is a `.env` file in the project root.

Create it through the Explorer — right-click the project root → **New File** → `.env`:

```dotenv
SF_COMPANY_ID=ACMECORP
SF_CLIENT_ID=replace-with-your-api-key
SF_USER_ID=api_user
SF_TOKEN_URL=https://apisalesdemo8.successfactors.com/oauth/token
SF_API_URL=https://apisalesdemo8.successfactors.com/odata/v2
SF_PRIVATE_KEY_PATH=keys/private_key.pem
SF_LOG_LEVEL=INFO
```

VS Code recognises the `.env` extension and applies syntax highlighting. Real values come from your SuccessFactors tenant in document 08; placeholders are fine for now.

In the terminal:

```bash
chmod 600 .env
grep -F '.env' .gitignore && echo "OK: .env is ignored"
```
- `chmod 600` — owner read and write only.
- `grep -F` — treat the pattern as a fixed string rather than a regular expression, so the dot means a literal dot.

Check the Explorer pane: `.env`, `.venv/` and `keys/` should appear greyed out, which is how VS Code shows Git-ignored files. That is a useful at-a-glance confirmation that nothing sensitive is tracked.

A `.env` file is **not** an environment. It is a text file that a library reads and loads *into* the environment at startup — which is what `python-dotenv` does.

## 10. Build `config.py`

Everything above, applied. Explorer → right-click `src` → **New File** → `config.py`:

```python
"""Configuration for the SuccessFactors integration.

All settings come from the process environment. A `.env` file in the
project root is loaded at import time for local development; in
production the variables are supplied by the service manager instead.

Validation happens once, at startup. A missing or malformed setting
raises ConfigError immediately rather than failing later in the run.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Project root is one level up from src/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# override=False means a real environment variable always wins over the
# file, which is what you want when systemd supplies the value.
load_dotenv(PROJECT_ROOT / ".env", override=False)


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def _require(name: str) -> str:
    """Return the value of an environment variable, or raise.

    Used for settings with no sensible default, where continuing
    without a value would only produce a confusing failure later.
    """
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise ConfigError(
            f"Required environment variable {name} is not set. "
            f"Add it to .env or export it before running."
        )
    return value.strip()


def _optional(name: str, default: str) -> str:
    """Return the value of an environment variable, or a default."""
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else default


def _require_path(name: str) -> Path:
    """Return a Path from an environment variable, verifying it exists."""
    path = Path(_require(name)).expanduser()

    if not path.is_absolute():
        # Resolve relative paths against the project root, not the current
        # working directory, so behaviour is identical whether launched
        # from VS Code, from src/, or by a systemd unit.
        path = PROJECT_ROOT / path

    if not path.exists():
        raise ConfigError(f"{name} points to {path}, which does not exist")

    return path


@dataclass(frozen=True)
class Config:
    """Validated configuration for one SuccessFactors environment."""

    company_id: str
    client_id: str
    user_id: str
    token_url: str
    api_url: str
    private_key_path: Path
    log_level: str
    http_timeout: float

    def __repr__(self) -> str:
        """Representation with the client ID truncated.

        Config objects end up in log lines and tracebacks. The client ID
        is not as sensitive as a private key, but there is no reason to
        print it in full.
        """
        return (
            f"Config(company_id={self.company_id!r}, "
            f"client_id={self.client_id[:6]}..., "
            f"user_id={self.user_id!r}, "
            f"token_url={self.token_url!r}, "
            f"private_key_path={self.private_key_path!r})"
        )


def load_config() -> Config:
    """Read, validate and return configuration. Raises ConfigError."""
    timeout_raw = _optional("SF_HTTP_TIMEOUT", "30")
    try:
        timeout = float(timeout_raw)
    except ValueError as exc:
        raise ConfigError(
            f"SF_HTTP_TIMEOUT must be a number, got {timeout_raw!r}"
        ) from exc

    token_url = _require("SF_TOKEN_URL")
    if not token_url.startswith("https://"):
        raise ConfigError(
            f"SF_TOKEN_URL must use https, got {token_url!r}. "
            f"Credentials must never traverse plain HTTP."
        )

    return Config(
        company_id=_require("SF_COMPANY_ID"),
        client_id=_require("SF_CLIENT_ID"),
        user_id=_require("SF_USER_ID"),
        token_url=token_url,
        api_url=_require("SF_API_URL"),
        private_key_path=_require_path("SF_PRIVATE_KEY_PATH"),
        log_level=_optional("SF_LOG_LEVEL", "INFO"),
        http_timeout=timeout,
    )


if __name__ == "__main__":
    try:
        cfg = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        raise SystemExit(1) from exc

    print("Configuration loaded successfully:")
    print(f"  {cfg}")
    print(f"  timeout: {cfg.http_timeout}s")
```

### 10.1 What each piece does

**`load_dotenv(..., override=False)`** — reads the `.env` file into `os.environ`. `override=False` means a variable already present in the real environment wins. Deliberate ordering: in production `systemd` or a container runtime supplies the values, and a stale `.env` left on the filesystem must not quietly take precedence.

**`PROJECT_ROOT = Path(__file__).resolve().parent.parent`** — `__file__` is this module's own path; `.resolve()` makes it absolute and follows symlinks; two `.parent` steps go from `src/config.py` to the project root. Building paths relative to the *module* rather than the working directory means the program behaves identically however it is launched — which matters specifically because VS Code runs files from the workspace root while a `systemd` unit might use anything.

**The leading underscore on `_require`** — section 2.2's convention: internal helper, not part of this module's public interface. The public interface is `load_config`, `Config` and `ConfigError`.

**`@dataclass(frozen=True)`** — a **decorator**, a function that modifies the class below it. `dataclass` generates `__init__`, `__eq__` and `__repr__` from the annotated fields, saving a page of boilerplate. `frozen=True` makes instances immutable: `cfg.company_id = "OTHER"` raises `FrozenInstanceError`. Section 2.1's point, enforced by the language.

**The custom `__repr__`** — overrides the generated one to truncate the client ID using the slicing from section 3.1. Secrets reach logs through `repr()` far more often than through deliberate printing, because tracebacks print the repr of every local variable — and so does VS Code's Variables pane.

**`{value!r}` in the f-strings** — the `!r` conversion applies `repr()` rather than `str()`. In an error message, `got '30 '` immediately reveals a trailing space that `got 30 ` would hide entirely. Section 3.2, applied.

**`raise ... from exc`** — exception chaining from section 7.2, preserving the original `ValueError` underneath the `ConfigError`.

**The `https://` check** — a deliberate refusal. Credentials over plain HTTP are visible to anything on the path, which you will see with your own eyes in document 07's packet capture.

### 10.2 Run it

With `config.py` open, press `Ctrl+F5`.

The `private_key_path` check fails, because `keys/private_key.pem` doesn't exist yet — that key is generated in document 04. Create a placeholder in the terminal:

```bash
touch keys/private_key.pem
```

Run again. Expected:

```
Configuration loaded successfully:
  Config(company_id='ACMECORP', client_id=replac..., user_id='api_user', ...)
  timeout: 30.0s
```

**Now run it under the debugger.** Put a breakpoint on the `return Config(` line in `load_config` and press `F5`. The Variables pane shows every validated value. In the **Debug Console**, type:

```python
_require("SF_COMPANY_ID")
os.environ.get("SF_LOG_LEVEL")
PROJECT_ROOT
```

You are calling your own functions inside the running program. For understanding how a module behaves, this beats adding print statements and re-running.

### 10.3 Watch it fail correctly

A configuration module is only as good as its error messages. Create `.vscode/launch.json` — Run and Debug pane → "create a launch.json file" → Python → Python File — and replace its contents with:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "config: normal",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/config.py",
      "console": "integratedTerminal"
    },
    {
      "name": "config: missing company ID",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/config.py",
      "console": "integratedTerminal",
      "env": { "SF_COMPANY_ID": "" }
    },
    {
      "name": "config: bad timeout",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/config.py",
      "console": "integratedTerminal",
      "env": { "SF_HTTP_TIMEOUT": "abc" }
    },
    {
      "name": "config: plain HTTP",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/config.py",
      "console": "integratedTerminal",
      "env": { "SF_TOKEN_URL": "http://example.com/oauth/token" }
    },
    {
      "name": "config: missing key file",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/config.py",
      "console": "integratedTerminal",
      "env": { "SF_PRIVATE_KEY_PATH": "keys/nope.pem" }
    },
    {
      "name": "main",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/main.py",
      "console": "integratedTerminal"
    }
  ]
}
```

- `"type": "debugpy"` — the debug adapter the Python extension provides.
- `"request": "launch"` — start a new process, as opposed to `"attach"` to a running one.
- `"program"` — the file to run.
- `"console": "integratedTerminal"` — run in the terminal rather than an internal console, so `input()` and terminal output behave normally.
- `"env"` — environment variables **for this launch only**, layered on top of your shell's. This is section 9.2's inheritance model, driven from the editor: VS Code places these in the child process's environment block and nowhere else.

Pick each configuration from the dropdown at the top of the Run and Debug pane and press `F5`. Each should print one clear line naming the exact variable, and exit with status 1.

The same thing from the terminal, if you prefer:

```bash
SF_COMPANY_ID="" python src/config.py; echo "exit status: $?"
```
- `VAR=value command` — set an environment variable for that single command only.
- `;` — run the next command regardless of the previous one's result.
- `$?` — the exit status of the last command. `0` means success; anything else is failure. `systemd` and cron inspect exactly this to decide whether a scheduled run failed, which is why getting it right now matters in Phase G.

### 10.4 Import it from another module

Explorer → right-click `src` → **New File** → `main.py`:

```python
"""Entry point. Currently just proves configuration loads."""

from config import Config, ConfigError, load_config


def describe(cfg: Config) -> None:
    """Print a short summary of the loaded configuration."""
    print(f"Company:   {cfg.company_id}")
    print(f"Token URL: {cfg.token_url}")
    print(f"API URL:   {cfg.api_url}")
    print(f"Key file:  {cfg.private_key_path}")


def main() -> None:
    try:
        cfg = load_config()
    except ConfigError as exc:
        print(f"Startup failed: {exc}")
        raise SystemExit(1) from exc

    describe(cfg)


if __name__ == "__main__":
    main()
```

Run the **"main"** launch configuration.

Note what did *not* happen: importing `config` printed none of its own demonstration output. That block sits under `if __name__ == "__main__"`, so it runs only when `config.py` is executed directly — section 6.2, working as designed.

If Pylance underlines `from config import ...` in red, it is because `src` isn't on the import path for analysis. Add to `.vscode/settings.json`:

```json
  "python.analysis.extraPaths": ["${workspaceFolder}/src"]
```

Proper package structure, which removes the need for this, arrives in Phase D when the module count justifies it.

Commit:

```bash
git add src/ .vscode/ .gitignore && git commit -m "Add validated configuration module"
```

## Verification checklist

Run each in the integrated terminal.

```bash
# 1. Valid configuration loads and exits 0
python src/config.py >/dev/null && echo "OK: loads cleanly"

# 2. Missing required value fails loudly with exit status 1
SF_CLIENT_ID="" python src/config.py >/dev/null 2>&1 || echo "OK: fails on missing value"

# 3. The object is immutable
python -c "
import sys; sys.path.insert(0, 'src')
from config import load_config
cfg = load_config()
try:
    cfg.company_id = 'HACKED'
    print('FAIL: config is mutable')
except Exception:
    print('OK: config is frozen')
"

# 4. repr() does not expose the full client ID
python -c "
import sys, os; sys.path.insert(0, 'src')
from config import load_config
full = os.environ.get('SF_CLIENT_ID', 'x' * 40)
print('OK: truncated' if full not in repr(load_config()) else 'FAIL: leaks')
"

# 5. Secrets stay out of git
git status --short --untracked-files=all | grep -E '^\?\? (\.env|keys/)' \
  && echo "FAIL: secrets visible to git" || echo "OK: secrets ignored"
```
- `>/dev/null` — discard standard output. `/dev/null` is a kernel device that accepts and discards everything written to it.
- `2>&1` — redirect file descriptor 2 (standard error) to wherever 1 (standard output) currently points.
- `||` — run the next command only if the previous one *failed*. The counterpart to `&&`.
- `sys.path.insert(0, 'src')` — prepend `src` to the import search path so the one-liner can find the module.

Also check the **Problems pane** (`Ctrl+Shift+M`): it should be empty for `src/`. Any remaining squiggle is Pylance telling you about a type mismatch worth understanding before moving on.

## What this gives you

- A validated, immutable configuration module that every later phase imports unchanged
- Variables, strings, bytes, dictionaries, functions, modules, exceptions and type hints — learned against code that stays in the project rather than exercises that get deleted
- A VS Code workflow you'll use for the rest of the build: interpreter selection, inline type checking, breakpoints, the Variables pane, the Debug Console, and launch configurations that vary the environment per run
- The `str`/`bytes` distinction established before Phase B, where getting it wrong is the single most common source of confusion
- A working model of the Linux process environment: what it is in memory, how inheritance works, what it protects against and what it doesn't
- Fail-fast startup validation, so a misconfiguration produces one clear line naming the variable instead of a traceback twenty minutes into a run

## Not covered yet

- **Logging** — `print()` is adequate for now; `SF_LOG_LEVEL` sits in the config waiting for it. Structured logging with levels and handlers arrives in document 16, alongside retries.
- **Multiple environments** — one `.env` works while there is one tenant. Separate dev/test/prod profiles, and selecting between them from the launch dropdown, come in Phase G.
- **Secrets managers** — section 9.3's honest limitation. The production path is `systemd` credentials or a vault; environment variables are right for this lab and wrong for production holding a signing key.
- **Testing** — `tests/` is still empty. Once there is logic worth asserting on (the XSLT transforms in Phase E), `pytest` and VS Code's Testing pane arrive properly rather than bolted on.
- **Classes beyond `@dataclass`** — inheritance, methods, properties. Introduced in Phase C where the OAuth client genuinely needs state (a cached token and its expiry), rather than taught in the abstract here.
- **Remote development** — if the build eventually runs on the mini PC rather than your laptop, VS Code's Remote-SSH extension edits files there over the SSH connection from [02-remote-access-ssh-rdp](../00-infrastructure/02-remote-access-ssh-rdp.md). Worth knowing it exists; not needed yet.
