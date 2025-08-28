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

