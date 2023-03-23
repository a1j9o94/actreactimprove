# actreactimprove
Expands upon the ideas in the ActReact Paper as well as Simon Wilson's Implementation by adding an addition element to the loop where the LLM is asked to evaluate it's performance and suggest new actions"

[ReAct: Synergizing Reasoning and Acting in Language Models | Hacker News (ycombinator.com)](https://news.ycombinator.com/item?id=35238937)

[A simple Python implementation of the ReAct pattern for LLMs | Simon Willison’s TILs](https://til.simonwillison.net/llms/python-react-pattern)

[Account Profile - API Ninjas (api-ninjas.com)](https://api-ninjas.com/profile)

# Here is an example run:

Question: What is the sum of the population of the 3 largest cities in the US during the term of our 17th president?

Thought: I need to find out who was the 17th president of the United States and what were the three largest cities in his presidency term. Then, I can look up the population of each city and sum them up.
Action: 
- wikipedia: 17th president of the United States
PAUSE

Observation: The 17th president of the United States was Andrew Johnson, who served from 1865 to 1869.

Action:
- wikipedia: List of United States cities by population
PAUSE

Observation: The three largest cities in the US during Andrew Johnson's presidency (1865-1869) were New York City (population of 1,174,779), Philadelphia (population of 565,529), and Brooklyn (population of 396,099).

Action:
- calculate: 1174779 + 565529 + 396099
PAUSE

Observation: The sum of the populations of the three largest cities during Andrew Johnson's presidency is 2,136,407.

Answer: The sum of the population of the three largest cities in the US during Andrew Johnson's presidency is 2,136,407.
Evaluation: Overall, the answer is accurate and follows a logical process to arrive at the required sum. However, here are a few ways that it could be improved:

1. Clarify the time period being referenced: While the question mentions the term of the 17th president, it might be helpful for the answer to repeat this information to ensure the reader has the proper context.

2. Include sources: While the answer provides information about the three largest cities during Andrew Jackson's presidency and their populations, it would be helpful to include links or sources to provide more information on where this data came from.

3. Utilize constants: Instead of typing out the population numbers to be summed up, it would be better practice to assign these values to named constants/variables, which would make it more readable and easier to modify if the question was phrased differently. For example:

```
NY_POPULATION = 1174779
PHILLY_POPULATION = 565529
BROOKLYN_POPULATION = 396099

total_population = NY_POPULATION + PHILLY_POPULATION + BROOKLYN_POPULATION
```

Using variables also makes the code easier to read and reduces the risk of typographical errors.
Improvement: Suggested improvement: historic_population(city, year)

Python code:

```
def historic_population(city, year):
    """
    Looks up the population of a given city and year.
    Uses the Population Reference Bureau's data, available at https://www.prb.org/international/indicator/population/table/.
    """
    import httpx
    response = httpx.get("https://api.prb.org/api/indicator/population/table", params={"gle_code": city, "year": year})
    data = response.json()
    population = data[0]["Value"]
    return population
```

With this new action, we can improve the answer by using it to simplify the code for finding the population values of the three cities:
```
NY_POPULATION = historic_population("USNY", 1865) # New York City
PHILLY_POPULATION = historic_population("USPA", 1865) # Philadelphia
BROOKLYN_POPULATION = historic_population("USNY", 1865) # Brooklyn (which was an independent city at the time)

total_population = NY_POPULATION + PHILLY_POPULATION + BROOKLYN_POPULATION
```

This not only makes the code more concise and easier to read, but it also allows us to easily modify the cities and years in the future if necessary.