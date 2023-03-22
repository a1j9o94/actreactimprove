import httpx
import re
import openai
import os
from dotenv import load_dotenv

# This code is Apache 2 licensed:
# https://www.apache.org/licenses/LICENSE-2.0

load_dotenv()
openai.api_key = os.environ.get("OPEN-AI-API-KEY")


class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages)
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)
        return completion.choices[0].message.content

    def evaluate(self, question, answer):
        evaluation_prompt = f"Evaluate the answer '{answer}' for the question '{question}', and provide a step-by-step breakdown of what could be improved."
        return self(evaluation_prompt)

    def improve(self, question, answer, evaluation):
        improvement_prompt = f"Considering the evaluation: '{evaluation}', improve the answer '{answer}' for the question '{question}' by suggesting a new action and its Python implementation."
        return self(improvement_prompt)


prompt = """
You run in a loop of Thought, Action, PAUSE, Observation, Evaluation, Improvement.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.
Evaluation will be a step-by-step breakdown of what could be improved.
Improvement will be a new action and its Python implementation. The actions should be something you expect to have to use again and should be generally useful

Your original available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

simon_blog_search:
e.g. simon_blog_search: Django
Search Simon's blog for that term

world_population:
e.g. world_population: France
Returns the population of the country


Youre first answer MUST only use these available actions. After the first one, you can start creating new ones.

Always look things up on Wikipedia if you have the opportunity to do so.
When suggesting new actions, think outside of the box and be very creative - the more creative the better!
When giving ways to improve, be very critical and break out at least 3 ways the answer could have been more helpful

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris.

Evaluation example:
Based on the evaluation, it's suggested to include the population of the capital city.
It could be improved by
- Suggesting things to do in the city
- Looking up average hotel prices in the city
- Pulling up recent news stories about the city

Suggested improvement: news: Paris
Python code:
def news(subject):
    return httpx.get("https://example.news.api.com/", params={"subject": subject}).json()["story1"]

""".strip()


action_re = re.compile('^Action: (\w+): (.*)$')


def query(question, max_turns=5):
    i = 0
    bot = ChatBot(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split(
            '\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception(
                    "Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            answer = result.strip()
            evaluation = bot.evaluate(question, answer)
            print("Evaluation:", evaluation)

            improvement = bot.improve(question, answer, evaluation)
            print("Improvement:", improvement)

            new_action_match = action_re.match(improvement)
            if new_action_match:
                action, action_code = new_action_match.groups()
                print(f"New action suggested: {action}\nPython code:\n{action_code}")
                # Implement the new action here or store it for later use
            return


def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]


def simon_blog_search(q):
    results = httpx.get("https://datasette.simonwillison.net/simonwillisonblog.json", params={
        "sql": """
        select
          blog_entry.title || ': ' || substr(html_strip_tags(blog_entry.body), 0, 1000) as text,
          blog_entry.created
        from
          blog_entry join blog_entry_fts on blog_entry.rowid = blog_entry_fts.rowid
        where
          blog_entry_fts match escape_fts(:q)
        order by
          blog_entry_fts.rank
        limit
          1""".strip(),
        "_shape": "array",
        "q": q,
    }).json()
    return results[0]["text"]


def calculate(what):
    return eval(what)

def world_population(city):
    api_url = 'https://api.api-ninjas.com/v1/city?name={}'.format(city)
    response = httpx.get(
        api_url, headers={'X-Api-Key': os.environ.get("NINJA-API-KEY")})
    if response.status_code == httpx.codes.ok:
        print(response.text)
        return response.json()['population']


known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "simon_blog_search": simon_blog_search,
    "world_population": world_population
}

if __name__ == '__main__':
    query("What is the sum of the population of the 3 largest cities in the US during the term of our 17th president?")