from browser_use.browser.browser import Browser
from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
import os

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), 'secrets.env')
load_dotenv(dotenv_path)

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["ANONYMIZED_TELEMETRY"] = "false"

# The model will only see the keys (x_name, x_password) but never the actual values
sensitive_data = {
    'username': os.getenv('EMAIL'),
    'password': os.getenv('PASSWORD'),
    'banking_username': os.getenv('BANKINGUSERNAME'),
    'banking_password': os.getenv('BANKINGPASSWORD')
}

from browser_use import Agent, SystemPrompt

class MySystemPrompt(SystemPrompt):
    def important_rules(self) -> str:
        # Get existing rules from parent class
        existing_rules = super().important_rules()

        # Add your custom rules
        new_rules = """
        You are a helpful navigation and action assistant.
        You must follow the user instructions exactly and must validate you are always obeying the instructions in the order the user specified.
        When scrolling in tabs with multiple sections you must make sure you CLICK ON THE SECTION YOU ARE TRYING TO SCROLL IN. 
        """

        # Make sure to use this pattern otherwise the exiting rules will be lost
        return f'{existing_rules}\n{new_rules}'



# Use the placeholder names in your task description
task = """
You are a financial advisor's assistant.
Go to http://localhost:8501/ and login with my username and password.
Then, do the following: 
Capture the current state of the accounts.
Sell all of Client C's NVIDIA shares and spend as much as possible on MS
If client does not have enough money or shares you should stop and move on to the next step.
You should then return to the main client menu and capture all my client metrics and print them out in a nice simple report.
Finally, when you are done, log out of the website.

Then, go to Gmail and log in with my credentials and draft an email. 
When using email interface, when entering who to address it to, each person's email should be entered seperately. After typing each individual person's email, you should type it and then hit enter before proceeding to the next person. 
The email must have the following:
Addressee are the following: pradeep.sundaram@morganstanley.com; mainak.saha@morganstanley.com; timothy.eng@morganstanley.com;
You should CC timothy.eng@outlook.com. 
The subject should be 'Sample banking transaction with a dummy app - no hands!' 
The body should contain, nicely formatted, the client metrics both before and after updated to reflect the changes you executed.
You should reformat the metrics before and after to be human readable - replace new lines with enter, escape sequences with their actual characters, etc. 
Make an additional note in the body saying Hi! and about how I didn't have to lift a finger to write the email, and about how cool Operator is and how potentially it could be quite powerful, given the correct guardrails.
Sign it Best, Tim

After doing all this make sure you've set up all the email components I've specified correctly. Do not send the email until all the above conditions have been met.
After doing that, send the email. 
Wait for it to send before closing. Check that it shows up in sent mail. 
"""

from browser_use.browser.context import BrowserContextConfig, BrowserContext

config = BrowserContextConfig(
    browser_window_size={'width': 1920, 'height': 1080},
    save_recording_path="recordingoutput",
    trace_path="."
)

browser = Browser()
context = BrowserContext(
    browser=browser,
    config=config,
)

llm = ChatOpenAI(
    model='gpt-4o',
    temperature=0.0,
)

# Pass the sensitive data to the agent
agent = Agent(
    browser_context=context,
    task=task,
    llm=llm,
    sensitive_data=sensitive_data,
    max_failures=10,
)

async def main():
    await agent.run()

if __name__ == '__main__':
    asyncio.run(main())