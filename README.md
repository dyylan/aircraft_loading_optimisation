# Aircraft Loading Problem
## Airbus Quantum Computing Challenge
The [Airbus Quantum Computing Challenge](https://www.airbus.com/innovation/airbus-quantum-computing-challenge/Problem-statements.html) is a set of problems which Airbus has designed where the challenge is to implement the solutions on a quantum computer. This project looks specifically at ***Problem Statement 5: Aircraft Loading Optimisation***. 

Try out the current version of the solver [here](https://airbus.dylanlewis.me). It currently does **not** work with IE or Edge. The server is only one vCPU, with 3 [gevent](http://www.gevent.org/index.html) workers, but it still manages the example optimisations with relative ease.

## Application details
The application uses the web micro-framework Flask to interact with the linear programming tools. Flask allows a simple index route, `templates/index.html`, to be defined in `main.py` with several forms defined in `app/forms.py`. These forms allow new settings to be input by the user. All the settings are saved to the client using session cookies so multiple client connections do not interfere with each other. These session cookies seem to be the reason the app does not work in IE or Edge. The data is saved to the client as a JSON object which is converted to Python objects for manipulation via the Block and BlockList classes located in `app/blocks.py`. JavaScript functions in `static/forms.js` use `fetch` to allow the client to request JSON objects containing the results of the linear programming steps from the server. The linear programs are contained in `app/lp.py`. We also map these linear programs to quadratic unconstrained binary optimisation (QUBO) problems. These are contained in `app/qubo.py`.

## Linear programs
There are currently two linear programs. The description in `_description.html` is in the webapp and provides an overview of the maths used in the problem. 

## QUBO programs
So far only one QUBO program has been implemented and the performance is very suboptimal. Currently, I am not sure why this is the case. The description of the mapping is in the webapp, source for the description is `_qubo.html`.

## Running locally for testing and development
Docker can be used to run this project locally or on a server, which may be easiest as it doesn't require any additional downloads. Install docker by following the [Docker installation guide](https://docs.docker.com/install/) for either Windows, Linux or MacOS. However, Docker is not required, and the project can be run locally if any of the linear programming solvers have been downloaded (GLPK, COIN-OR, or the PULP-CBC sovler).

### The environment variables
Once the repo has been cloned and Docker has been installed, make a `.env` file with four environment variables:
```
FLASK_APP=main.py
FLASK_DEBUG=0
SOLVER=glpk
SECRET_KEY=supersecretunguessablekey
```
`FLASK_DEBUG` can be set to 1 if you are not using Docker. This makes testing and developing easier. To run in the Docker, the `SOLVER` environment variable must be set to `glpk`. However, if running locally, `default` or `coin` can also be used if you have the correct packages installed on your computer.

### With Docker
You can now simply build the image, which I have named "airbus" here, from within the project directory: 
```
docker build -t airbus .
```
Then run the image 
```
docker run --name airbus -p 8000:5000 --rm --env-file=.env airbus
```
This builds a container which is accessible on port 8000. 

Even more simply, you can just run the `deploy.sh` script, with arguments for name, port and whether it is a redeployment: 
```
sh ./deploy.sh airbus 8000 redeploy logs
```
Which will also do `git pull` and `docker image prune`. The `redeploy` argument means the docker container with name `airbus` will be stopped. Simply remove `redeploy` to prevent this. `logs` at the end of the line means that the logs are entered on deployment, to exit the logs (without stopping the container), simply press CTRL+c. See the docker [documentation](https://docs.docker.com/get-started/part2/) and specifically the docker [logs documentation](https://docs.docker.com/v17.09/engine/reference/commandline/logs/) for more information about docker and container logs.

Visit `127.0.0.1:8000`/`localhost:8000` in a web browser to use the application. Currently, IE and Edge do **not** work. 

### Without Docker
To run from the terminal with the web micro-framework [Flask](http://flask.pocoo.org/), it is easiest to use pipenv to install all the requirements. Pipenv creates a virtual environment for Python and manages the packages and versions required. It essentially combines venv and pip into one package and is really easy to use. See [this guide](https://pipenv.readthedocs.io/en/latest/install/) for installing pipenv. 

In the project directory, run 
```
pipenv install
```
followed by
```
pipenv run flask run
```
The environment variables should be picked up automatically and the Flask application should be running on port 5000. So visit `127.0.0.1:5000`/`localhost:5000` in a web browser to use the application. Currently, IE and Edge do **not** work. If `FLASK_DEBUG` is set to 1, any changes to the `.py` files should automatically trigger a reload of the Flask built-in development server without having to restart the Flask application manually. 