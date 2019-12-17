# GISTQUERY

Gistquery is a utility to query a single user's GitHub gists

## Usage

`gistquery <username>`

Where `<username>` is the Github user's username.

The first time you query a user's gist will register the current ones in a local
sqlite3 database located in `/tmp/gists.db` and display the gists for that user.
 
Subsequent executions for the same username will tell you if a new gist has been added or removed and
it is synced with the local database. 

## The util is based on Python 3.7.4 it presumes that it is already available on the system.
### For a potential python version manager please check out the [pyenv](https://github.com/pyenv/pyenv) pages.



## Developing

### Setting up

```sh
$ python setup.py install
$ make init
```
### Project utilizes [pipenv](https://realpython.com/pipenv-guide/) for managing dependencies and virtual environments.
For accessing the the developer env after running `make init` please run.

```
pipenv shell
``` 


## Testing
```
make test
```

## Build/Install

The build/install process utilizes  [pyinstaller](https://www.pyinstaller.org) for packaging and creating a self executable file.
```
make build
```

## Exit codes

* User not found: 255
* User has not published any gists: 1
* Success (first or subsequent queries): 0

## License

GNU General Public License v3.0