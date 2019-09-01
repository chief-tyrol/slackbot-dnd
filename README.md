# slackbot-dnd [![Build status][build-icon]][build-link] 

[build-link]: https://jenkins.gryphon.zone/job/chief-tyrol/job/slackbot-dnd/job/master/
[build-icon]: https://jenkins.gryphon.zone/buildStatus/icon?job=chief-tyrol%2Fslackbot-dnd%2Fmaster

# Developer Setup

All commands are run from the project root directory, unless specified otherwise

### 1) Create Python virtual environment

```bash
python3 -m venv venv
```

### 2) Activate Python virtual environment

```bash
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install --upgrade --compile -r requirements.txt
```


### 4) Deactivate Python virtual environment

```bash
deactivate
```