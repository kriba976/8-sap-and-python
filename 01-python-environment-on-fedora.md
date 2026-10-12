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
# Python + SAP — Step 1: The Python Environment on Fedora

Goal: set up the working environment for the entire build — interpreter, isolated project environment, package manager, version control, editor — and understand what each piece actually does rather than copying commands. By the end you have the directory that every later document writes into, and you can explain what happens between typing `python3 app.py` and seeing output.

This is foundation work, but it is not filler. Roughly half the "it works on my machine" problems in Python integration work are environment problems: the wrong interpreter, a package installed into the wrong place, a `PATH` that resolves differently under `systemd` than in your shell. Those are much cheaper to understand now than to debug at 2am when the extractor fails on a schedule.

Shared Linux concepts (`sudo`, `dnf`, `systemctl`, terminal basics) are explained in [01-backup-sync-setup](../00-infrastructure/01-backup-sync-setup.md) and not repeated here.

## Architecture

```
   your source file                  app.py  (text)
            │
            │  python3 app.py
            ▼
   ┌──────────────────────────────────────────────┐
   │ CPython interpreter                           │
   │                                               │
   │   parse  →  compile to bytecode  →  execute   │
   │                    │                          │
   │                    └── cached in __pycache__  │
   └───────────────────┬──────────────────────────┘
                       │ imports resolved via sys.path
                       ▼
   ┌──────────────────────────────────────────────┐
   │ .venv/                 ← project-local        │
   │   bin/python  →  /usr/bin/python3  (symlink)  │
   │   lib/python3.X/site-packages/                │
   │       requests/, lxml/, psycopg/ …            │
   └──────────────────────────────────────────────┘
                       │ falls back to
                       ▼
   /usr/lib64/python3.X/        ← standard library
```

The key idea the diagram encodes: **a virtual environment is not a second Python.** It is a directory containing a symlink to the system interpreter plus its own package folder, and a mechanism for making that interpreter look there first.

## 0. One-time: confirm what Fedora already gives you

Fedora ships Python 3 as part of the base system — `dnf` itself is written in Python, which has a consequence you need to respect in section 6.

```bash
python3 --version
```

Expect `Python 3.12.x` or later on a current Fedora.

```bash
type -a python3
```
- `type` — a shell builtin that reports how the shell would interpret a given name: alias, function, builtin, or an executable file on `PATH`.
- `-a` — show *all* matches in `PATH` order, not just the first one that wins.

Typical output:

```
python3 is /usr/bin/python3
```

If you see several lines, the first is the one that actually runs. That is the most common cause of "I installed the package but Python says it isn't there."

Follow the symlink chain to the real binary:

```bash
readlink -f /usr/bin/python3
```
- `readlink` — print what a symbolic link points to.
- `-f` — follow the chain all the way to the final real file, resolving every intermediate link.

You'll get something like `/usr/bin/python3.12`. So `python3` is a link to a specifically versioned binary, which is how Fedora upgrades the minor version without breaking every script that says `python3`.

Note there is deliberately **no plain `python`** command on Fedora:

```bash
type -a python
```

This returns "not found", and that is correct, not broken. The ambiguity of `python` meaning Python 2 on some systems and Python 3 on others caused enough damage that Fedora simply declines to provide it. Inside a virtual environment it will exist and point unambiguously at your project's interpreter — section 5.

## 1. What the interpreter actually does

CPython — the reference implementation and what Fedora ships — is not a pure interpreter in the line-by-line sense, and it is not a compiler to machine code either. It does both, in two stages:

```
app.py  ──parse──►  AST  ──compile──►  bytecode  ──execute──►  result
                                          │
                                   cached as .pyc
```

1. **Parse** the source text into an abstract syntax tree.
2. **Compile** that tree into *bytecode* — a compact instruction set for a virtual machine, not for your CPU.
3. **Execute** the bytecode on the Python virtual machine, a loop that dispatches one instruction at a time.

See it directly:

```bash
python3 -c "import dis; dis.dis('x = 1 + 2')"
```
- `-c` — run the following string as a program instead of reading a file.
- `dis` — the standard library's bytecode disassembler.

Output:

```
  0           RESUME                   0
  1           LOAD_CONST               0 (3)
              STORE_NAME               0 (x)
              RETURN_CONST             1 (None)
```

Two things worth noticing. First, these are stack-machine instructions — `LOAD_CONST` pushes a value, `STORE_NAME` pops it into a variable. Second, `1 + 2` has already become the constant `3`: the compiler folded it at compile time. Python does optimise, just not aggressively.

**Why this matters practically:** the compile step is why the first import of a large library feels slow and subsequent ones don't. Python caches the bytecode:

```bash
find /usr/lib64/python3.*/ -name '__pycache__' -maxdepth 2 | head -3
```
- `find` — search a directory tree.
- `-name '__pycache__'` — match directories with this name. Quoted so the shell doesn't try to expand it.
- `-maxdepth 2` — don't descend more than two levels, keeping the search fast.

Inside those directories are `.pyc` files — cached bytecode, named with the interpreter version so a Python upgrade invalidates them automatically. You never manage these by hand; they're mentioned because you will see them appear in your project directory and should know they are disposable build artefacts, which is why they go in `.gitignore` in section 7.

## 2. Install the development packages

The base Python is present, but a few pieces needed for development are not.

```bash
sudo dnf install python3-pip python3-devel
```
- `python3-pip` — the package installer. Usually present, included for completeness.
- `python3-devel` — C header files for Python. Needed when a package has a C extension that must be compiled during installation. Many packages ship precompiled wheels and never need this, but `lxml` and `psycopg` — both required later in this build — may fall back to compiling from source. Installing this now avoids a confusing wall of compiler errors in Phase E.

While you're here, install the build toolchain those extensions need:

```bash
sudo dnf install gcc libxml2-devel libxslt-devel libpq-devel
```
- `gcc` — the C compiler.
- `libxml2-devel` / `libxslt-devel` — development headers for the XML and XSLT C libraries. `lxml` is a Python wrapper around these; the actual XML parsing and XSLT transformation in Phase E is done by this C code, not by Python.
- `libpq-devel` — development headers for PostgreSQL's client library, used by `psycopg` in Phase F.

Installing these now rather than when each phase arrives means the later documents stay focused on their own subject.

Verify pip:

```bash
python3 -m pip --version
```
- `-m pip` — run the `pip` *module* using this specific interpreter, rather than invoking a `pip` executable from `PATH`.

**Always use `python3 -m pip`, never bare `pip`.** The reason is the `type -a` lesson from section 0: a bare `pip` is some executable somewhere on `PATH`, and which interpreter it installs into is a guess. `python3 -m pip` is unambiguous — it installs into whichever interpreter you just named. This single habit prevents a large fraction of Python environment confusion.

## 3. How the shell finds `python3`

Worth a short detour, because it explains both section 2's warning and a failure mode you'll hit when running your extractor under `systemd` in Phase G.

```bash
echo "$PATH" | tr ':' '\n'
```
- `echo "$PATH"` — print the `PATH` environment variable. Quoted so the shell doesn't split it on whitespace.
- `|` — pipe the output into the next command.
- `tr ':' '\n'` — translate characters: replace every colon with a newline, putting each directory on its own line.

You'll see something like:

```
/home/you/.local/bin
/usr/local/bin
/usr/bin
/bin
```

When you type a command, the shell walks this list **in order** and runs the first match. `PATH` is an ordinary environment variable, which means it is inherited by child processes and can differ between contexts — your interactive shell, a cron job, and a `systemd` service all see different values. A script that works in your terminal and fails under `systemd` with "command not found" is almost always this.

Check where a command resolves without running it:

```bash
command -v python3
```
- `command -v` — print the path that would be used for a name. Functionally similar to `which`, but a POSIX shell builtin rather than an external program, so it is available everywhere and also sees shell functions and aliases.

## 4. Create the project

```bash
mkdir -p ~/projects/sf-integration
cd ~/projects/sf-integration
```

One directory for the entire build. Everything from the OAuth client through to the API gateway configuration lives here, growing over the phases. The final shape is in Phase H; don't create it now.

Starting structure:

```bash
mkdir -p src keys docs tests
```

- `src/` — Python source.
- `keys/` — private keys and certificates. Never committed; see section 7.
- `docs/` — notes specific to the code, distinct from this documentation series.
- `tests/` — test files, from Phase E onward.

Lock down the key directory immediately, same reasoning as document 04 of this block:

```bash
chmod 700 keys
```
- `700` — octal permissions: owner read+write+execute, group nothing, others nothing. On a directory, the execute bit means "may enter and traverse", so this is "only I can even list the contents."

## 5. Virtual environments — what they actually are

### 5.1 The problem being solved

Python installs packages into a shared directory. Without isolation:

```
system Python
    └── site-packages/
            requests 2.28      ← project A needs this
            requests 2.31      ← impossible; only one version can exist
```

Two projects needing different versions of the same package cannot coexist. Worse, on Fedora, `dnf` is itself a Python program using system packages — installing or upgrading something system-wide with pip can break your package manager, which is a genuinely unpleasant afternoon.

### 5.2 Create one

```bash
python3 -m venv .venv
```
- `-m venv` — run the standard library's `venv` module.
- `.venv` — the directory to create. The leading dot makes it hidden in `ls`, and this name is the de facto convention that VS Code, PyCharm and most tooling auto-detect.

### 5.3 Look inside it before activating

This is the part normally taken on faith. Don't.

```bash
ls -l .venv/
```

```
bin/        include/        lib/        lib64 -> lib        pyvenv.cfg
```

```bash
cat .venv/pyvenv.cfg
```
- `cat` — print a file's contents.

```
home = /usr/bin
include-system-site-packages = false
version = 3.12.7
executable = /usr/bin/python3.12
```

That is the entire configuration. It records which real interpreter this environment is based on, and whether to also look in the system's package directory (`false` — full isolation).

```bash
ls -l .venv/bin/
```

```
activate
pip
python -> python3
python3 -> /usr/bin/python3
```

**`.venv/bin/python3` is a symlink to the system interpreter.** There is no copy of Python here. The isolation comes from somewhere else entirely:

```bash
ls .venv/lib/python3.12/site-packages/
```

An empty (or near-empty) directory. *That* is the isolation — a private place for this project's packages.

The mechanism tying them together: when CPython starts, it looks at the path of the executable that launched it, walks up the directory tree looking for a `pyvenv.cfg`, and if it finds one, sets its package search path to that environment's `site-packages` instead of the system's. The symlink's *location* is what does the work, not the binary it points to.

### 5.4 Activate it, and understand what activation does

```bash
source .venv/bin/activate
```
- `source` — execute a script **in the current shell** rather than in a child process. This matters enormously: a normal script runs in a subshell, and any environment changes it makes die when it exits. `source` lets the script modify your current shell's environment.

Your prompt changes:

```
(.venv) you@fedora:~/projects/sf-integration$
```

Read the script to see what just happened:

```bash
grep -E 'VIRTUAL_ENV=|PATH=|PS1=' .venv/bin/activate
```
- `grep` — search text for matching lines.
- `-E` — extended regular expressions, so `|` means alternation.
- The pattern — find the three assignments that do the real work.

The three things activation does:

1. **`VIRTUAL_ENV="/home/you/projects/sf-integration/.venv"`** — an environment variable recording which environment is active. Tools read this.
2. **`PATH="$VIRTUAL_ENV/bin:$PATH"`** — *prepends* the environment's `bin` directory to `PATH`. Now `python` and `pip` resolve to the environment's copies first, by the exact first-match rule from section 3.
3. **`PS1="(.venv) $PS1"`** — prepends the environment name to your shell prompt, purely so you can see at a glance which environment is active.

Activation is nothing but three environment variable changes. There is no magic, no daemon, no system state. Confirm it:

```bash
command -v python
python -c "import sys; print(sys.prefix); print(sys.base_prefix)"
```
- `sys.prefix` — where this interpreter looks for packages: your `.venv`.
- `sys.base_prefix` — the underlying installation: `/usr`.

When those two differ, you're in a virtual environment. That comparison is the programmatic way to check, and it is what most tools use.

```bash
deactivate
```

A shell *function* defined by the activate script, which restores the saved `PATH` and `PS1` and unsets `VIRTUAL_ENV`. That is why there is no `deactivate` file in `bin/` — it isn't a program.

Reactivate before continuing:

```bash
source .venv/bin/activate
```

### 5.5 Where `import` actually looks

```bash
python -c "import sys; [print(p) for p in sys.path]"
```

```
                                       ← empty string: the current directory
/usr/lib64/python312.zip
/usr/lib64/python3.12
/usr/lib64/python3.12/lib-dynload
/home/you/projects/sf-integration/.venv/lib/python3.12/site-packages
```

`sys.path` is an ordinary Python list, searched in order on every `import`. Note the standard library still comes from `/usr/lib64` — the virtual environment doesn't duplicate it, only third-party packages.

Note also the empty string at the top, meaning the current directory. This is why a file you name `requests.py` in your project will shadow the real `requests` library and produce baffling errors. Don't name files after packages.

## 6. Installing packages

```bash
python -m pip install requests
```

Note `python`, not `python3` — inside an active environment they are the same thing, and using `python` makes it obvious you're relying on the environment.

Watch where it lands:

```bash
python -c "import requests; print(requests.__file__)"
```
- `__file__` — a module attribute holding the path of the file it was loaded from.

The path is inside your `.venv`, not `/usr`. The isolation is real and you have now proven it rather than assumed it.

```bash
python -m pip list
```

`requests` plus its dependencies — `urllib3`, `certifi`, `charset-normalizer`, `idna`. Note **`certifi`**: a bundled set of trusted root certificates. Python does not use Fedora's system trust store by default, which becomes important in document 07 when TLS verification fails against your own CA and the fix is not where you'd expect.

### 6.1 Never use `sudo pip`

If you try to install into the system Python on a current Fedora:

```
error: externally-managed-environment
```

This is **PEP 668** working as designed. Fedora marks its system Python as managed by `dnf`, and pip refuses to interfere. The protection exists because pip overwriting a `dnf`-installed library can break `dnf` itself, leaving you unable to use the package manager to fix the package manager.

The correct response is never `--break-system-packages`. It is: use a virtual environment, which you now have.

### 6.2 Recording dependencies

```bash
python -m pip freeze > requirements.txt
cat requirements.txt
```
- `freeze` — output installed packages in exactly the format `install` accepts, with versions pinned.
- `>` — redirect output to a file, overwriting it.

```
certifi==2025.8.3
charset-normalizer==3.4.1
idna==3.10
requests==2.32.4
urllib3==2.3.0
```

Every version pinned, including transitive dependencies. Someone else — or you on a rebuilt machine — reproduces the environment exactly:

```bash
python -m pip install -r requirements.txt
```
- `-r` — read requirements from a file.

**Pinned versus unpinned, and why it matters here.** `requests==2.32.4` is reproducible but requires manual updates for security patches. `requests>=2.32` gets patches automatically but means two installs a month apart may behave differently. For an integration that runs unattended against a production SuccessFactors tenant, reproducibility wins: pin, and update deliberately. This is the same argument behind locking transport content versions in Cloud Integration rather than always taking latest.

## 7. Version control

```bash
git init
```
- `git init` — create a repository in the current directory (a `.git` subdirectory holding the entire history).

Identify yourself, if you haven't globally:

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

Without `--global` these apply to this repository only, which is useful when work and personal identities differ.

Now the file that matters most:

```bash
cat > .gitignore <<'EOF'
# Virtual environment — rebuildable from requirements.txt
.venv/

# Bytecode cache
__pycache__/
*.pyc

# Secrets and keys — NEVER commit
.env
keys/
*.key
*.pem
*.p12

# Editor
.vscode/
EOF
```
- `cat > file <<'EOF'` — a **heredoc**: feed everything up to the line `EOF` into `cat`, which writes it to the file.
- The **quotes around `'EOF'`** are not decoration. Unquoted, the shell would expand any `$variable` or backtick inside the block. Quoted, the text is written literally. Always quote the delimiter unless you specifically want expansion.

Verify the exclusions actually work before you ever have a real key:

```bash
touch keys/test.key .env
git status --short
```
- `touch` — create empty files (or update timestamps on existing ones).
- `git status` — show what Git sees.
- `--short` — compact output.

Neither file should appear. If they do, the `.gitignore` is wrong — fix it now, while the files are empty and harmless.

```bash
rm keys/test.key .env
```

**Why this is section 7 and not section 12.** A private key committed to Git is not fixed by deleting it in a later commit; the object remains in history and in every clone. The only real remedy is rotating the key. Setting up `.gitignore` before any secret exists costs two minutes; the alternative costs an incident report. The SuccessFactors signing key in Phase C is exactly the kind of thing this protects.

First commit:

```bash
git add .gitignore requirements.txt
git commit -m "Initial project structure"
```
- `add` — stage files for the next commit.
- `commit` — record the staged state.
- `-m` — the commit message inline, rather than opening an editor.

## 8. VS Code

Install from Microsoft's official Fedora repository per their published instructions, then add two extensions:

- **Python** (Microsoft) — debugging, test running, environment discovery.
- **Pylance** (Microsoft) — the language server providing completion, type checking and inline errors.

Open the project:

```bash
code .
```
- `code` — the VS Code CLI.
- `.` — the current directory, opened as the workspace root.

**Select the interpreter**, which is the one piece of configuration that matters:

```
Ctrl+Shift+P  →  "Python: Select Interpreter"  →  ./.venv/bin/python
```

Without this, VS Code uses the system Python, Pylance reports `requests` as unresolved, and the debugger runs against the wrong packages. The symptom is squiggly red underlines on imports that work fine in the terminal — now you know exactly why.

Persist it for the workspace:

```bash
mkdir -p .vscode
cat > .vscode/settings.json <<'EOF'
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "files.trimTrailingWhitespace": true
}
EOF
```

- `python.defaultInterpreterPath` — which interpreter to use.
- `${workspaceFolder}` — a VS Code variable resolving to the project root, keeping the setting portable.
- `python.terminal.activateEnvironment` — automatically run `source .venv/bin/activate` in integrated terminals.

Note `.vscode/` is in `.gitignore`, so this stays local. Some teams commit it deliberately to share settings; either is defensible, but keep secrets out of it in that case.

## 9. Prove the whole chain works

```bash
cat > src/check_env.py <<'EOF'
import sys
import requests

print(f"Interpreter:  {sys.executable}")
print(f"Version:      {sys.version.split()[0]}")
print(f"In venv:      {sys.prefix != sys.base_prefix}")
print(f"requests:     {requests.__version__}")
EOF
```

Run it:

```bash
python src/check_env.py
```

```
Interpreter:  /home/you/projects/sf-integration/.venv/bin/python
Version:      3.12.7
In venv:      True
requests:     2.32.4
```

Three Python features are in there, each formally introduced in document 02, but worth naming now since you've just run them:

- **`import`** — load a module and bind it to a name, resolved through the `sys.path` list from section 5.5.
- **`f"..."`** — an f-string: a literal where `{expression}` is evaluated and substituted. The main tool for building URLs, SQL fragments and XML later.
- **`sys.prefix != sys.base_prefix`** — a comparison producing a boolean, the exact virtual environment check from section 5.4.

A `__pycache__` directory has now appeared — the bytecode cache from section 1, already excluded from Git.

## Verification checklist

```bash
# 1. The active interpreter is the project's, not the system's
command -v python | grep -q ".venv" && echo "OK: venv interpreter active"

# 2. Packages resolve from the venv
python -c "import requests, sys; assert '.venv' in requests.__file__; print('OK: isolated packages')"

# 3. Secrets cannot be committed
touch .env keys/x.key
test -z "$(git status --short --untracked-files=all | grep -E '\.env|keys/')" \
  && echo "OK: secrets ignored" || echo "FAIL: check .gitignore"
rm .env keys/x.key

# 4. The environment is reproducible
test -s requirements.txt && echo "OK: requirements.txt present"
```
- `grep -q` — quiet mode: produce no output, just an exit status. Useful in conditionals.
- `assert` — a Python statement that raises an error if the condition is false. A terse way to make a script fail loudly.
- `test -z "$(...)"` — true when the command's output is empty.
- `test -s` — true when the file exists and is non-empty.
- `--untracked-files=all` — list individual untracked files rather than collapsing directories, so the check can't be fooled.

## What this gives you

- A project directory that every subsequent document in this block builds into
- An isolated Python environment you can explain mechanically — symlink, `pyvenv.cfg`, `PATH` prepend, `sys.path` — rather than treat as a ritual
- The `python -m pip` habit, which eliminates a whole class of "installed but not found" problems
- Version control with secrets excluded *before* any secret exists
- The build dependencies for `lxml` and `psycopg` already in place, so Phases E and F don't stall on compiler errors

## Not covered yet

- **The Python language itself** — document 02 covers variables, strings, dictionaries, functions, modules and exceptions, and you use them to build the real `config.py` that the rest of the project reads its settings from.
- **Multiple Python versions side by side** — if you later need to test against 3.11 and 3.13, `pyenv` or Fedora's parallel-installable `python3.11` packages handle it. Not needed while targeting one version.
- **`pyproject.toml` and modern packaging** — `requirements.txt` is adequate for an application you run rather than distribute. Revisited in Phase G when the API becomes a deployable service.
- **Dependency locking with hashes** — `pip freeze` pins versions but not artefact hashes, so it doesn't protect against a compromised package index. `pip-tools` or `uv` add that. Worth adopting before anything touches production.
- **Running Python under `systemd`** — where the `PATH` lesson from section 3 stops being theoretical. Phase G, document 29.
