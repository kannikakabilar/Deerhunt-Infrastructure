
#  Official Deerhunt Infrastructure

This is the official repo of the Deerhunt Website developed and run by the UTM Robotics Club. This is an open source project maintained by our students.

The Deerhunt Infrastructure project is a full stack application built for the purpose of hosting and running AI competitions.

For more on the project structure, check out the [use-case diagram](https://docs.google.com/drawings/d/1g27NYuGy7EOh-BjOJ5ivY8iGT_Yk4H1zTYuXLu_msW8/edit?usp=sharing) and [storyboard](https://docs.google.com/drawings/d/1T8kFRi2JBQRj8-ogstJT3UTrvXxLSBnhUbPJa4i5ucg/edit?usp=sharing).
## Documentation
All documentation is written with the help of [mkdocs](https://www.mkdocs.org/), a python pip package which allows us to write documentation in markdown and convert it all to a beautiful static site that can be hosted. It is included in the `requirements.txt` file so your virtual environment should have it installed. You can find everything under the `docs/` folder. You will see a `mkdocs.yml` file as well as another `docs/` folder where all the actual markdown files are. 
```
docs/
├── docs/
│   └── index.md
└── mkdocs.yml
```
Mkdocs comes with a built in static server that you can host locally and see your documentation changes happen instantly in the browser.
```
$ (venv) cd docs
$ (venv) mkdocs serve
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.08 seconds
INFO     -  [14:05:26] Serving on http://127.0.0.1:8000/
```
Open your favorite web browser and navigate to `http://127.0.0.1:8000/`. 
Happy documenting!

## Folder Structure
```
.
├── deerhunt/
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   ├── README.md
│   └── src/
├── tests/
│   ├── ref
│   └── test_auth.py
├── server/
│   ├── app.py
│   └── requirements.txt
├── install.sh
└── README.md
```
**deerhunt/**: Everything to do with the frontend lives here. You will find npm related files here as well as the frontend source files.

**server/**: All backend source files live in this folder.

**tests/**: All unittests at least for the backend will live here. Currently empty but will be populated soon. Make sure you are familiar with  [Pytest Framework](https://docs.pytest.org/en/6.2.x/#).

## Dependencies
- A unix based computer
- git
- python3+
- npm

 
##  Development Setup Instructions
I encourage you to go through the install script to understand what it is doing before running it. Once it runs you should have a folder called **venv/** created. After running the install script you have to source your venv folder and your terminal should look something like this:
```
$ (venv) adl@Cronos ~/git/deerhunt2020/infrastructure
``` 
If you need to read up on python virtual environments you can do so [here](https://docs.python.org/3/tutorial/venv.html).


### Ubuntu / Debian
It is important that you have a Linux installation such as Ubuntu / Debian which uses [apt](https://linux.die.net/man/8/aptitude) as its package manager since the script uses it. Also make sure you keep your system packages up to date.
```
$ sudo apt update
$ sudo apt upgrade -y
$ cd Deerhunt-Infrastructure
$ ./install.sh
$ source venv/bin/activate
```

### Mac OSX
Make sure you have [Homebrew](https://brew.sh/) installed and updated before running the script below.
```
$ brew update
$ brew doctor
$ cd Deerhunt-Infrastructure
$ ./install.sh
$ source venv/bin/activate
```

### Windows
Windows users can technically develop locally in their windows environment but we highly recommend using Linux for consistency. You can partition your hard-drive and install Linux next to your Windows or you can use WSL. There is WSL 1 and WSL 2. We recommend WSL 2 because it is newer but either one should still work.

#### WSL (Windows Subsystem for Linux)
##### What is WSL 2:
https://docs.microsoft.com/en-us/windows/wsl/about


##### Enable WSL 2:
https://docs.microsoft.com/en-us/windows/wsl/install-win10

Using WSL, users should be able to open a Linux Shell in linux, and follow the steps from "Ubuntu/Debian".

## Contributing
Pull requests are welcomed. Check out our [Deerhunt Infrastructure Trello board](https://trello.com/b/hRKytFnG/deerhunt-infra-board) for outlined changes that the team is looking to work on. 

A timeline for project tasks is outlined [here](https://docs.google.com/spreadsheets/d/1Sa-3uzRZ_Iij_ZZ43PbxutlVTsftbJ5iLF-hyRE50l0/edit?usp=sharing).
