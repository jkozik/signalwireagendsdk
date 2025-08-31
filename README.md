# Using SignalWire AI Agent, build IVR that uses Google Web Search
At [Cluecon 2025 conference](https://www.cluecon.com/schedule-2025), the SignalWire team was introducing their new [AI Agents SDK](https://developer.signalwire.com/sdks/agents-sdk/). This is a Python environment for an AI-based IVR. On a poster at the conference there was an example use case of a web search bot.  I implemented it, and saved the code in this repository.   

<img width="400" height="600" alt="image" src="https://github.com/user-attachments/assets/c57bf083-bba7-4c9c-be1e-b7d90e3bfbbb" />

On the registration table the same Python script was distributed to the conference on little index cards.


<img width="400" height="600" alt="image" src="https://github.com/user-attachments/assets/754eb3b7-b9a0-4626-96d3-63d292a9b7db" />

In the [SignalWire AI Agent SDK QuickStart](https://developer.signalwire.com/sdks/agents-sdk/quickstart/#create-your-first-agent) they named this short program `dev-agent.py`.  Thus I will use the same name in this repository. 

## Summary
For my reference and perhaps the benefit of others, I recorded the steps I followed to get this work.  Here's a summary.  The following sections give lots of details.  

- Clone Repository
- Get GOOGLE API Key and Search Engine ID
- Setup .env with key, ID and SignalWire Auth data
- On server my server 192.168.100.128, build and run `dev-agent.py` using `docker compose build` then `docker compose up -d`
- verify log files ok
- setup firewall to route port 3000 to my private reverse proxy
- setup reverse proxy to map URL https://*.swaig.kozik.net -> http://192.168.100.128:3000
- Verify URL  http://jkozik:XXXXXX:3000
- Verify  URL https://jkozik:XXXXXXXX@swaig.kozik.net  (tests reverse proxy, Let's Encrypt)
- Provision URL above into a SignalWire Phone number's `When a call comes in`
- Call the phone number and verify interaction

Note: I have a reverse proxy on my home LAN that leverages Let's Encrypt for https URLs.  Adding an additional mapping for this service is easy.  To me, much easier than `ngrok`. 

# My setup -- A picture plus the steps I followed
To run this script, I put it on my home server in a Docker container.  My home network has a reverse proxy that manages incoming https:// URLs, mapping specific URLs to internal servers/ports. This lets me dedicate the subdomain https://swaig.xxxxxx.net for linkage between the script and SignalWire.  

Here's a picture of my setup.

<img width="1294" height="731" alt="image" src="https://github.com/user-attachments/assets/f5656eff-6888-4099-92d8-d475da7ed87d" />


## dev-agent.py
On my home server, I setup a project and created the file dev-agent.py
```python
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
- The default dev-agent.py generated a new Authentication Password, leading to the need to update the SignalWire provisioning after every code change.  My .env setup makes tinkering much easier to do. I put the SWML authenication, GOOGLE API key and id in a .env file.  See end of README for more details.
- I setup a venv and ran this program from the command line.  It is good for initial setup, I prefer things in Docker containers


## Docker setup
In Docker containers, I find that it makes it easier for me to share with others and re-create if I ever want to run them again.
My `Dockerfile` file is straight forward.
```dockerfile
(.venv) jkozik@u2004:~/projects/swaia-google$ cat Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
```
```shell
(.venv) jkozik@u2004:~/projects/swaia-google$ docker images
REPOSITORY                                                                                              TAG       IMAGE ID       CREATED         SIZE
swaia-google-dev-agent                                                                                  latest    1587f1f0049e   24 hours ago    235MB
```
An image size of 235MB is not bad.

My `docker-compose.yml` file has some important things:
```
(.venv) jkozik@u2004:~/projects/swaia-google$ cat docker-compose.yml
```
```yaml
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
I have GOOGLE and SignalWire Markup environment variables held in a .env file.  The script will not work without these correctly provisioned.  See sections below for instructions for setting these variables. 

## docker-compose.yml
The build is very straight forward:
```shell
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
Once the image is built, run it.
```shell
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
- I XXX'd out the secrets.  The AgentBase class shares the keys in the logfile.  If you don't supply them, they will get generated and logged here.
- From the logfile, one can see that agent_base runs on port 3000 of a FastAPI-based web service.  

## Verify dev-agent.py 
From a terminal on the Home LAN, run the command below to verify that port 3000 can be accessed. 
```shell
(.venv) jkozik@u2004:~/projects/swaia-google$ curl http://jkozik:XXXXXXXXXXXXXXXX@192.168.100.128:3000 | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1638  100  1638    0     0  17968      0 --:--:-- --:--:-- --:--:-- 18200
```
```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "answer": {}
      },
      {
        "ai": {
          "prompt": {
            "pom": [
              {
                "body": "you are Franklin, the web search bot.",
                "title": "role"
              },
              {
                "bullets": [
                  "Ask the user what they want to search for on the web"
                ],
                "title": "instructions"
              },
              {
                "body": "You can search the internet for current, accurate information on any topic using the web_search tool.",
                "bullets": [
                  "Use the web_search tool when users ask for information you need to look up",
                  "Search for news, current events, product information, or any current data",
                  "Summarize search results in a clear, helpful way",
                  "Include relevant URLs so users can read more if interested"
                ],
                "title": "Web Search Capability"
              }
            ],
            "temperature": 0.3,
            "top_p": 1,
            "barge_confidence": 0,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1
          },
          "SWAIG": {
            "functions": [
              {
                "function": "web_search",
                "description": "Search the web for information on any topic and return detailed results with content from multiple sources",
                "parameters": {
                  "type": "object",
                  "properties": {
                    "query": {
                      "type": "string",
                      "description": "The search query - what you want to find information about"
                    }
                  }
                },
                "web_hook_url": "http://jkozik:XXXXXXXXXXX@192.168.100.128:3000/swaig/?__token=QzNGdjFiSlZFNGlmdWphMDlwRXXXXXXXXXXmNoLjE3NTYzMzk0OTUuNmNhMzRhZmIuMTI1ZDZmNzdiNTRhMGM2NA=="
              }
            ],
            "defaults": {
              "web_hook_url": "http://jkozik:XXXXXXXXXXXXXXXXXXXX@192.168.100.128:3000/swaig/"
            }
          },
          "params": {},
          "languages": [
            {
              "name": "English",
              "code": "en-US",
              "voice": "rime.spore"
            }
          ],
          "global_data": {
            "web_search_enabled": true,
            "search_provider": "Google Custom Search"
          }
        }
      }
    ]
  }
}
```
Note a few things:
- the URL includes a user id, a password and points to port 3000
- Piping the output through jq, one can see that this agent is web hook and is feeding prompt information to SignalWire.

From a terminal window running on a host outside of the home LAN, verify that the https:// version of the URL works.  This verifies both the Let's Encrypt TLS processing and the reverse proxy URL to port mapping. 
```
(.venv) jkozik@u2004:~/projects/swaia-google$ curl https://jkozik:bbVOlu80VNfIG-ydx4B-sYBW-x4wA7JuPvATbd6eHHU@swaig.kozik.net
```
```json
{"version": "1.0.0", "sections": {"main": [{"answer": {}}, {"ai": {"prompt": {"pom": [{"body": "you are Franklin, the web search bot.", "title": "role"}, {"bullets": ["Ask the user what they want to search for on the web"], "title": "instructions"}, {"body": "You can search the internet for current, accurate information on any topic using the web_search tool.", "bullets": ["Use the web_search tool when users ask for information you need to look up", "Search for news, current events, product information, or any current data", "Summarize search results in a clear, helpful way", "Include relevant URLs so users can read more if interested"], "title": "Web Search Capability"}], "temperature": 0.3, "top_p": 1.0, "barge_confidence": 0.0, "presence_penalty": 0.1, "frequency_penalty": 0.1}, "SWAIG": {"functions": [{"function": "web_search", "description": "Search the web for information on any topic and return detailed results with content from multiple sources", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "The search query - what you want to find information about"}}}, "web_hook_url": "http://jkozik:bbVOlu80VNfIG-ydx4B-sYBW-x4wA7JuPvATbd6eHHU@swaig.kozik.net/swaig/?__token=T25oWW9FcEpkRWItRVdmbnViNjE4dy53ZWJfc2VhcmNoLjE3NTYzNDAyOTYuMGExODExZWMuYjg4NDY2Y2FkZjY1ZjQ3Mw=="}], "defaults": {"web_hook_url": "http://jkozik:bbVOlu80VNfIG-ydx4B-sYBW-x4wA7JuPvATbd6eHHU@swaig.kozik.net/swaig/"}}, "params": {}, "languages": [{"name": "English", "code": "en-US", "voice": "rime.spore"}], "global_data": {"web_search_enabled": true, "search_provider": "Google Custom Search"}}}]}}

```
This worked, but I didn't pretty print it. Note: no need to reference port 3000; the reverse proxy maps from port 443 to 3000

## Provision the URL into SignalWire
The URL used in the above test needs to be provisioned into the SignalWire.  From the SignalWire dashboard, in my case that's https://jkozik.signalwire.com/dashboard  (password protected) select on the left hand column:  `Phone Number` -> `Handle Calls Using` as `a SWML Script`.  The URL needs to be inserted into the `When a call comes in` field. I used an existing phone number.  You may need to buy your own if you don't already have one. 
<img width="1630" height="766" alt="image" src="https://github.com/user-attachments/assets/5f4d21dd-f706-4cfc-911f-f186a9b5fd05" />

Save the changes and call the phone number.  It is interesting to look at the docker log file.  You'll see a web hook call per interaction with the service.  

## Summary

The dev-agent.py python program is a really good "Hello World" example script to help me learn the SignalWire AI Agent SDK.  For me, the next step is to study some of the [Agent API Examples](https://github.com/signalwire/signalwire-agents/blob/main/examples/README.md)




# Setting up Google API Keys
To setup the Google keys for Custom Search API access, you need to get a google cloud API Key and a Search Engine Key.  

To start, at the [Google Cloud Console](https://console.cloud.google.com/apis/dashboard?project=vaulted-night-270914).  

<img width="1655" height="827" alt="image" src="https://github.com/user-attachments/assets/db002906-82e5-4de0-8603-c7cdc779c648" />

It will prompt to setup a project, I picked "My First Project" -- the default name.  Then I went to the Credentials on the lefthand side. On the top, click on `+ Create Credentials` and select `API Key`.  

<img width="1536" height="629" alt="image" src="https://github.com/user-attachments/assets/d2e6b7c4-dd24-4c7a-bea1-3feb6287447c" />

I created the key, called `API Key` with no restrictions. Set the API key into the .env file as `GOOGLE_SEARCH_API_KEY`

To get a Search Engine ID, go to the [Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all) control panel and `Add` 

<img width="1475" height="921" alt="image" src="https://github.com/user-attachments/assets/374349b7-3eeb-4046-8e9c-44ff5bb4a3d1" />

I called it `google`.  When created you'll see Search Engine ID.  Set the ID into the .env file as `GOOGLE_SEARCH_ENGINE_ID`

<img width="857" height="741" alt="image" src="https://github.com/user-attachments/assets/f6831bbf-2d34-451b-ba98-28647c086b85" />

## SWML Basic Authentication
To work with SignalWire AI Agent SDK, user and a password need to be setup.  By default, the AgentBase class library will generate a default user name of `signalwire` and a > 20 character random password.  Each time, the class initializes, a new password is generated.  This is a pain, because that password needs to be inserted into the URL from SignalWire's   `When a Call Comes in` script parameter.

Therefore, I use the environement variables `SWML_BASIC_AUTH_USER` and `SWML_BASIC_AUTH_PASSWORD` in .env.

If the SignalWire provisioning disagrees with these environment variables, a call to the SignalWire phone number returns "Sorry that number cannot be reached."

# References
- [Setting up API keys](https://support.google.com/googleapi/answer/6158862?hl=en)
- [Create a search engine](https://support.google.com/programmable-search/answer/11082370?hl=en&ref_topic=4513742&sjid=14720713324191360097-NC)
- [SignalWire AI Agent SDK QuickStart](https://developer.signalwire.com/sdks/agents-sdk/quickstart/#create-your-first-agent) 
- [SignalWire Agents SDK](https://developer.signalwire.com/sdks/agents-sdk/)
- [SignalWire AI Agent SDK Examples](https://github.com/signalwire/signalwire-agents/blob/main/examples/README.md)
- [Your AI Agent Deserves More Than a Webhook](https://share.signalwire.com/a-full-ai-framework-for-voice-not-just-a-prompt-playground?ecid=ACsprvtll5GcOXPzhhgJX4T1y7E2wq2hs4tSkUFYZ8irgLpBSA9VgwEOKWPk7pbgzfkh6AC85ADf&utm_campaign=17777493-Agent%20SDK%20Series%20Launch&utm_medium=email&_hsenc=p2ANqtz--JOx3ywMr5DfGFy4eWpFwP8mrVWTnXB-Oip9bF1zaCMxsVsenvvgCCETYn2lgeaI4QFv4D1LHUevZJFM0a8g-uMUEchA&_hsmi=377993165&utm_content=377993165&utm_source=hs_email)





















