import openai
import os
import json
import pickle

with open('secrets_keys.json') as f:
    secrets = json.load(f)
  
os.environ['OPENAI_API_KEY'] = secrets['openai']
cache_path = (
    "cache.pkl"  # embeddings will be saved/loaded here
)
PROMPT_TEMPLATE = '''Generate JSON data with data extracted from this doc

doc = """{text}"""

This person's name is {name}.
Extract this into a JSON dict in this format
{{
"about": Where does this person work and what is this person's title (string),
"building": 1 or 2 sentences of what ideas this person is building or hacking on at the hackathon this weekend (string),
}}

data = {{
    "about":'''

# except FileNotFoundError:
#     precomputed_cache_path = (
#         "https://cdn.openai.com/API/examples/data/snli_embedding_cache.pkl"
#     )

    #embedding_cache = pd.read_pickle(precomputed_embedding_cache_path)

def info_extract(text, name):
    # print(os.getcwd())
    if not os.path.isfile("cache.pkl"):
        with open("cache.pkl",'wb') as file:
            a = {'hi':'hi'}
            pickle.dump(a, file)
    with open(cache_path, "rb") as f:
        cache = pickle.load(f)      

    prompt = PROMPT_TEMPLATE.format(text=text, name=name)
    if text not in cache.keys():
        print("Not in cache, getting embedding...")
        cache[text] = text_generation(prompt)
        with open(cache_path, "wb") as cache_file:
            pickle.dump(cache, cache_file)
    #answers = text_generation(prompt)
    answers = cache[text]
    answers = answers.split('}')[0]
    answers = '{"about":' + answers.strip() + '}'
    # print(answers)
    # try:
    data = json.loads(answers)
    assert all([i in data for i in ('about', 'building')])
    return data
    # except:
    #     return {}

def text_generation(prompt):
    # send GPT-3 a prompt and get the response
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt,
      temperature=0.7,
      max_tokens=1000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0)
    return response['choices'][0]['text']