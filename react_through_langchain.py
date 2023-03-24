from langchain.llms import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from dotenv import load_dotenv

if __name__ == '__main__':
   load_dotenv()
   llm = OpenAI(temperature=0)
   tools = load_tools(["serpapi", "llm-math", "wikipedia"], llm=llm, top_k_results=5)
   agent = initialize_agent(tools, llm=llm, agent="zero-shot-react-description", verbose=True)
   agent.run("Who was the 17th president of the united states?")