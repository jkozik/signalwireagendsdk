# Build AI Agent in Python to Google Search, using SignalWire Agents SDK
Using the SignalWire SDK, this python script interacts with the SignalWire SWML script mechanism to control an AI-based IVR.  This script was taken from the stand up poster at the conference.  It implements a Google web search.  A basic application, sort of like a Hell World application for SignalWire's Agents SDK.

My first reaction was:  this looks really easy.  I want to give it a try.

![IMG_8117](https://github.com/user-attachments/assets/c57bf083-bba7-4c9c-be1e-b7d90e3bfbbb)

On the registration table the same Python script was distributed to the conference on little index cards.

![agentssdkcard082725](https://github.com/user-attachments/assets/754eb3b7-b9a0-4626-96d3-63d292a9b7db)

## dev-agent.py
On my home server, I setup a project and created the file dev-agent.py
```
(.venv) jkozik@u2004:~/projects/swaia-google$ cat dev-agent.py
import os
from dotenv import load_dotenv, find_dotenv
from signalwire_agents import AgentBase

#load_dotenv(find_dotenv())
load_dotenv()

# Create an agent
agent = AgentBase(name="franklin")

# Add some basic capabilities
agent.prompt_add_section("role", "you are Franklin, the web search bot.")
agent.prompt_add_section("instructions",
                         bullets=["Ask the user what they want to search for on the web"])

agent.add_language("English", "en-US", "rime.spore")

print("os.getenv test")
print( f"{os.getenv('GOOGLE_SEARCH_API_KEY')=}")
agent.add_skill("web_search", {
    "api_key": os.getenv('GOOGLE_SEARCH_API_KEY'),
    "search_engine_id": os.getenv('GOOGLE_SEARCH_ENGINE_ID')
})

if __name__ == "__main__":
    agent.run()

(.venv) jkozik@u2004:~/projects/swaia-google$
```
Note a few things:
- I put the GOOGLE API key and id in a .env file
- Just getting started, I created a virtual environment (venv).  Setup not shown

## My setup
To run this script, I put it on my home server in a Docker container.  I have a reverse proxy that manages a LetEncrypt based reverse proxy, letting me dedicate a subdomain for linkage between the script and SignalWire.  

Here's a picture of my setup.

<img width="1289" height="729" alt="image" src="https://github.com/user-attachments/assets/2e909739-2de3-4ace-aed2-9e2544ed46b8" />

## Docker setup
As a personal preferene, I like putting scripts like this, that is ones that run as an API with a REST interface on a dedicated port, I like putting them into docker containers.  It makes it easier for me to share with others and re-create if I ever want to run them again.
My docker file is really simple:
```
(.venv) jkozik@u2004:~/projects/swaia-google$ cat Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

(.venv) jkozik@u2004:~/projects/swaia-google$ docker images
REPOSITORY                                                                                              TAG       IMAGE ID       CREATED         SIZE
swaia-google-dev-agent                                                                                  latest    1587f1f0049e   24 hours ago    235MB
```
My docker-compose.yml file has some important things:
```
(.venv) jkozik@u2004:~/projects/swaia-google$ cat docker-compose.yml
version: '3.8'

services:
  dev-agent:
    build: .
    container_name: swaia-google-agent
    ports:
      - "3000:3000"
    environment:
      - GOOGLE_SEARCH_API_KEY=${GOOGLE_SEARCH_API_KEY}
      - GOOGLE_SEARCH_ENGINE_ID=${GOOGLE_SEARCH_ENGINE_ID}
      - SWML_BASIC_AUTH_USER=${SWML_BASIC_AUTH_USER}
      - SWML_BASIC_AUTH_PASSWORD=${SWML_BASIC_AUTH_PASSWORD}
    volumes:
      - ./.env:/app/.env:ro
    stdin_open: true
    tty: true
    restart: unless-stopped(
```
I have GOOGLE and SignalWire Markup environment variables.  I have a .env file with the secrets.  The script will not work without these.

## docker-compose.yml
The build is very straight forward:
```
(.venv) jkozik@u2004:~/projects/swaia-google$ docker compose build --no-cache
[+] Building 27.7s (11/11) FINISHED                                                                                                                                docker:default
 => [dev-agent internal] load build definition from Dockerfile                                                                                                               0.0s
 => => transferring dockerfile: 205B                                                                                                                                         0.0s
 => [dev-agent internal] load metadata for docker.io/library/python:3.11-slim                                                                                                0.8s
 => [dev-agent auth] library/python:pull token for registry-1.docker.io                                                                                                      0.0s
 => [dev-agent internal] load .dockerignore                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                              0.0s
 => [dev-agent 1/5] FROM docker.io/library/python:3.11-slim@sha256:1d6131b5d479888b43200645e03a78443c7157efbdb730e6b48129740727c312                                          0.0s
 => [dev-agent internal] load build context                                                                                                                                  1.5s
 => => transferring context: 423.68kB                                                                                                                                        1.4s
 => CACHED [dev-agent 2/5] WORKDIR /app                                                                                                                                      0.0s
 => [dev-agent 3/5] COPY requirements.txt .                                                                                                                                  0.1s
 => [dev-agent 4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                                                      21.0s
 => [dev-agent 5/5] COPY . .                                                                                                                                                 1.8s
 => [dev-agent] exporting to image                                                                                                                                           2.5s
 => => exporting layers                                                                                                                                                      2.5s
 => => writing image sha256:169cf8805043d8187c4e90dcaf2bcb7861c623e607f3e6018c9ffdc594615fba                                                                                 0.0s
 => => naming to docker.io/library/swaia-google-dev-agent                                                                                                                    0.0s
(.venv) jkozik@u2004:~/projects/swaia-google$
```
Once the image it built, run it.
```
(.venv) jkozik@u2004:~/projects/swaia-google$ docker compose up -d
[+] Running 1/1
 ✔ Container swaia-google-agent  Started                                                                                                                                     0.7s
(.venv) jkozik@u2004:~/projects/swaia-google$ docker compose logs
swaia-google-agent  | [20:49:43] INFO     security_config (info:72) security_config_loaded (service=SWMLService, ssl_enabled=False, domain=None, allowed_hosts=['*'], cors_origins=['*'], max_request_size=10485760, rate_limit=60, use_hsts=True, has_basic_auth=True)
swaia-google-agent  | [20:49:43] INFO     swml_service    (info:72) service_initializing (service=franklin, route=, host=0.0.0.0, port=3000)
swaia-google-agent  | [20:49:43] INFO     agent_base      (info:72) agent_initializing (agent=franklin, route=/, host=0.0.0.0, port=3000)
swaia-google-agent  | os.getenv test
swaia-google-agent  | os.getenv('GOOGLE_SEARCH_API_KEY')='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
swaia-google-agent  | [20:49:43] INFO     skill_manager   (info:72) Successfully loaded skill instance 'web_search_257ec295f507f4fff_web_search' (skill: 'web_search')
swaia-google-agent  | [20:49:43] INFO     agent_base      (info:72) agent_starting (agent=franklin, url=http://localhost:3000, username=jkozik, password_length=43, auth_source=environment, ssl_enabled=False)
swaia-google-agent  | Agent 'franklin' is available at:
swaia-google-agent  | URL: http://localhost:3000
swaia-google-agent  | Basic Auth: jkozik:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (source: environment)
swaia-google-agent  | INFO:     Started server process [1]
swaia-google-agent  | INFO:     Waiting for application startup.
swaia-google-agent  | INFO:     Application startup complete.
swaia-google-agent  | INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
```
Note a couple things:
- I XXX'd out the secrets.  The AgentBase class shares the keys in the logfile.  If you don't supply them, they will get generated.
- You'll need to consult the logfile to complete the SignalWire integration
