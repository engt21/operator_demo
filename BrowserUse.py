import asyncio
import os
import sys
import logging
import streamlit as st

# Set telemetry variable early
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Optionally load .env before browser_use config executes
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), 'secrets.env')
load_dotenv(dotenv_path)

# Create custom Streamlit logging handler that supports streaming via st.chat_message
class StreamlitHandler(logging.Handler):
    def __init__(self, placeholder=None):
        super().__init__()
        # placeholder is no longer used for buffering log lines
        self.log_placeholder = placeholder
    def emit(self, record):
        log_entry = self.format(record)
        # Each log entry is streamed as a new assistant chat message
        with st.chat_message("assistant"):
            st.write(log_entry)

# Setup custom logging BEFORE importing browser_use modules
# Create handler without a placeholder initially
streamlit_handler = StreamlitHandler(placeholder=None)
streamlit_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(message)s')
streamlit_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Clear existing root logger handlers and add our handler
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(streamlit_handler)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

# Import browser_use modules (they may set up their own loggers)
from browser_use.browser.browser import Browser
from langchain_openai import ChatOpenAI
from browser_use import Agent, SystemPrompt
from browser_use.browser.context import BrowserContextConfig, BrowserContext

# Force browser_use logger to propagate (so our handler sees its logs)
browser_use_logger = logging.getLogger("browser_use")
browser_use_logger.propagate = True

# Set ProactorEventLoop on Windows
if __name__ == "__main__" and os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), 'secrets.env')
load_dotenv(dotenv_path)

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# Define sensitive data
sensitive_data = {
    'email': os.getenv('EMAIL'),
    'email_password': os.getenv('EMAILPASSWORD'),
    'banking_username': os.getenv('BANKINGUSERNAME'),
    'banking_password': os.getenv('BANKINGPASSWORD')
}

# Define custom SystemPrompt
class MySystemPrompt(SystemPrompt):
    def important_rules(self) -> str:
        existing_rules = super().important_rules()
        new_rules = """
        You are a helpful navigation and action assistant.
        You must follow the user instructions exactly and must validate you are always obeying the instructions in the order the user specified.
        When scrolling in tabs with multiple sections you must make sure you CLICK ON THE SECTION YOU ARE TRYING TO SCROLL IN.
        If you get stuck, go back to the top of the page. 
        """
        return f'{existing_rules}\n{new_rules}'

test_steps = ""

dummy_fa_app_ux_test_framework_task = f"""
You are are helpful robotic process automation tester. 
I will provide you with a task that you are to test on a given app. 

You must always start by going to http://localhost:8501/ and logging in with my username and password for the banking site, and always finish with logging out of the site after the below steps are complete.

Here is the specific test goal and the steps you should take:
"""

ux_test_buy_enough_task = """
You are testing a financial advisor order entry system. You are to test the ability to buy shares for a client if they have enough funds.
- Buy 20 shares of Morgan Stanley for Client B.
- Ensure that the transaction is successful as they have enough investment balance. You should capture the exact text of the resulting message.
"""

ux_test_buy_task_not_enough = """
You are testing a financial advisor order entry system. You are to test the ability to buy shares for a client if they do not have enough funds.
- Buy 100000 shares of Morgan for Client B. 
- This should fail as they do not have enough money. You should capture the exact text of the resulting message.
"""

ux_test_sell_not_enough_task = """
You are testing a financial advisor order entry system. You are to test the ability to sell shares for a client if they do not have enough shares.
- Attempt to sell 10 shares of Microsoft for Client A. 
- This should fail as they do not own any Microsoft shares. You should capture the exact text of the resulting message.
"""

ux_test_sell_task = """
You are testing a financial advisor order entry system. You are to test the ability to sell shares for a client if they have enough shares. 
- Sell all of Client C's NVIDIA shares. You should capture the exact text of the resulting message. 
"""

#
# Then, go to Gmail and log in with my credentials and draft an email.
# When using email interface, when entering who to address it to, each person's email should be entered seperately. After typing each individual person's email, you should type it and then hit enter before proceeding to the next person.
# The email must have the following:
# Addressee are the following: pradeep.sundaram@morganstanley.com; mainak.saha@morganstanley.com; timothy.eng@morganstanley.com;
# You should CC timothy.eng@outlook.com.
# The subject should be 'Sample banking transaction with a dummy app - no hands!'
# The body should contain, nicely formatted, the client metrics both before and after updated to reflect the changes you executed.
# You should reformat the metrics before and after to be human readable - replace new lines with enter, escape sequences with their actual characters, etc.
# Make an additional note in the body saying Hi! and about how I didn't have to lift a finger to write the email, and about how cool Operator is and how potentially it could be quite powerful, given the correct guardrails.
# Sign it Best, Tim
#
# After doing all this make sure you've set up all the email components I've specified correctly. Do not send the email until all the above conditions have been met.
# After doing that, send the email.
# Wait for it to send before closing. Check that it shows up in sent mail.
#

# Streamlit UI
st.title("MS Operator")

# Initialize session state for chat input
if 'chat_input_value' not in st.session_state:
    st.session_state.chat_input_value = ""

# task_mappings = {
#     "Buy shares success": ux_test_buy_enough_task,
#     "Buy shares fail": ux_test_buy_task_not_enough,
#     "Sell shares success": ux_test_sell_task,
#     "Sell shares fail": ux_test_sell_not_enough_task,
# }
#
# with st.sidebar:
#     test_task_key = st.selectbox("Select a test task", list(task_mappings.keys()), placeholder="Choose a task")
#     test_steps = task_mappings.get(test_task_key)
#     task = dummy_fa_app_ux_test_framework_task + test_steps

task = st.chat_input("User task:")

#
# if test_task:
#     task = test_task
#
# else:
#     task = st.chat_input("Enter your task:")

# Create a placeholder at the bottom for log output (no longer used by our custom handler)
log_placeholder = st.empty()
# (Optional) You can assign this to the handler if needed:
streamlit_handler.log_placeholder = log_placeholder
if task:

    with st.chat_message("user"):
        st.write(task)

    # Browser and context setup
    config = BrowserContextConfig(
        # browser_window_size={'width': 1920, 'height': 1080},
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

    from browser_use import Controller, ActionResult

    # Initialize the controller
    controller = Controller()

    @controller.action('Ask user for confirmation whenever you click a button')
    def ask_human(question: str) -> str:
        root_logger.info("IN CONTROLLER ASK HUMAN")
        answer = input(f'\n{question}\nInput: ')
        root_logger.info(answer)
        return ActionResult(extracted_content=answer)

    # Pass the sensitive data to the agent
    agent = Agent(
        browser_context=context,
        task=task,
        llm=llm,
        sensitive_data=sensitive_data,
        max_failures=10,
        # generate_gif=test_task_key + ".gif",
        controller=controller,
    )

    # Re-add the logging handler (if needed)
    root_logger.addHandler(streamlit_handler)

    async def run_agent():
        await agent.run()

    asyncio.run(run_agent())
