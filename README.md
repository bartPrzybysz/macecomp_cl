# macecomp

A command line tool for managing the MACE COMP system

## Installation

#### For usage
``` bash
git clone https://github.com/bartPrzybysz/macecomp.git

cd macecomp

python setup.py install
```

#### For development
``` bash
pip install pipenv

git clone https://github.com/bartPrzybysz/macecomp.git

cd macecomp

pipenv install
```

## Configuration

Requires a json file in the following format:

``` json
{
    "DATABASE": {
        "host": "database hostname here",
        "database": "name of macecomp database here",
        "user": "database username here",
        "password": "username password here"
    },
    "REST": {
        "url": "https://franciscan.blackboard.com",
        "key": "Application Key (provided on BB REST registration)",
        "secret": "Secret (Provided on BB REST registration)"
    }
}
```

To view current configuration:
``` bash
macecomp config
```

To configure:
``` bash
macecomp config <path to file>.json
```

## Usage

#### Viewing help messages
``` bash
macecomp -h
```
``` bash
macecomp config -h
```
``` bash
macecomp upload-transcript -h
```

#### Running commands

``` bash
macecomp assign-questions
```
``` bash
macecomp upload-transcript <name of transcript file>.xlsx
```

