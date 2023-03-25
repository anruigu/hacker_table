import openai
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from gpt3 import info_extract
import pandas as pd
import gspread
import df2gspread as d2g

with open('secrets.json') as f:
    secrets = json.load(f)
  
openai.api_key = secrets['openai']
slack_token = secrets['slack']


client = WebClient(token=slack_token)
# get all messages in the "gpt4-hackathon" channel
channel_name = "intros"
conversation_id = None
try:
    # Call the conversations.list method using the WebClient
    for result in client.conversations_list():
        if conversation_id is not None:
            break 
        for channel in result["channels"]:
            print(channel["name"])
            if channel["name"] == channel_name:
                conversation_id = channel["id"]
                # print(conversation_id)
                #Print result
                print(f"Found conversation ID: {conversation_id}") # save this ID
                break
except SlackApiError as e:
    print(f"Error: {e}")

# Store conversation history
conversation_history = []
# ID of the channel you want to send the message to
channel_id = "C04EH9VQRFG"

try:
    # Call the conversations.history method using the WebClient
    # conversations.history returns the first 100 messages by default
    # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
    result = client.conversations_history(channel=channel_id)

    conversation_history = result["messages"]

    # Print results
    print("{} messages found in {}".format(len(conversation_history), channel_id))

except SlackApiError as e:
    print("Error creating conversation: {}".format(e))

filename = 'test'
N_ROWS = len(conversation_history)
res = pd.DataFrame(columns=['name', 'email','about','building'], index=range(N_ROWS))
NUM_FIELDS = len(res.columns) - 1
counter = 0
# make data table
for convo in conversation_history:
    # res.iloc[idx, 1:] = re.split(r'[0-9]+\*!\*: ', raw_ans)[1:]
    user_id = convo['user']
    try:
        # Call the users.info method using the WebClient
        result = client.users_info(
            user=user_id
        )
        name = result['user']['profile']['real_name_normalized']
        try:
            email = result['user']['profile']['email']
        except KeyError:
            continue # not a real user
        res.iloc[counter, 0] = name
        res.iloc[counter, 1] = email
    except SlackApiError as e:
        print("Error fetching conversations: {}".format(e))
    convo_s = json.dumps(convo)
    raw_ans = info_extract(convo_s, name) # .replace('\n','')
    # print(raw_ans)
    res.iloc[counter, 2] = raw_ans['about']
    res.iloc[counter, 3] = raw_ans['building']
    counter+=1

res.to_csv("{}.csv".format(filename))