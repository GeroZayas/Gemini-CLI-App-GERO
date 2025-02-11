from google import genai 
from google.genai import types
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich import print
# from rich.live import Live
# from rich.text import Text
# from rich.layout import Layout
import sys
import time
import threading
from datetime import datetime
from icecream import ic
import pyperclip
import dotenv

dotenv.load_dotenv()

# ============== GLOBALS ==================
MODEL = "gemini-2.0-flash"


SESSION_TIMESTAMP = f"{datetime.now():%Y-%m-%d %H-%M-%S}"

ic(SESSION_TIMESTAMP)

# ============== HELPER FUNCTIONS ==================

def input_no_echo(prompt: str = "", move_cursor_up: int = 2) -> str:
    print(prompt, end="")
    user_input= input()
    sys.stdout.write('\033[F \033[F')  # Move cursor up n lines
    sys.stdout.write('\033[K')  # Clear the line
    return user_input

# ANIMATION functions
def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def spinner(stop):
    spinner = spinning_cursor()
    while not stop():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        sys.stdout.write('\b')
        time.sleep(0.1)

# ============== WHOLE CONVERSATION TO BE SAVED TO LOCAL MACHINE ==================
CONVERSATION = f"CHAT - {SESSION_TIMESTAMP}\n"

def save_conversation(conversation: str)-> str:
    with open(f"./GEMINI_CHATS/{SESSION_TIMESTAMP}_{MODEL}_Chat.md", "w+", encoding="utf-8") as file:
        file.write(conversation)
    return "Conversation saved..."

# CHAT HISTORY of USER QUESTIONS to be passed to the LLM as memory
order_counter = 0
chat_memory_user_questions:dict = {}

# =================================================================
api_key = os.environ.get("GEMINI_API_KEY")


# =================================================================
query_prompt= "[bold cyan]Insert query ('quit' or 'q' for exiting):[/bold cyan]\n>>> "
user_settings_prompt= ("[bold blue]Insert name and preferences:[/bold blue]\n"
                       "[purple]My name is John, I want you to teach me ...[/purple]")

# =================================================================
print(user_settings_prompt)
USER_SETTINGS: str = input(">>> ")
SYSTEM_INSTRUCTION: str = "You are a helpful assistant and this is valuable information \
    about the user interacting with you: " + USER_SETTINGS
# =================================================================

config=types.GenerateContentConfig(
        system_instruction=USER_SETTINGS,
        temperature=0.0)

client = genai.Client(api_key=api_key)
console = Console()

# =================================================================
# =================================================================
program_on = True

while program_on:
    
    user_input = input_no_echo(prompt=query_prompt)
    console.print(Panel(user_input, title="User", border_style="blue", highlight=True ))
    
    order_counter += 1
    chat_memory_user_questions[order_counter] = user_input
    
    # console.print(chat_memory_user_questions)
    
    prompt = f"""
    Use this as context for the whole chat and to remember what the user has said before,
    because this is the chat history of your conversation with the user in order:
    {chat_memory_user_questions}
    Do not repeat the chat history unless explicitly asked by the user. Be friendly and funny.
    Explain concepts briefly but accurately. Explain using metaphors, analogies and examples.
    Give always real-world scenarios with code examples that could be useful in production environments.
    Keep always a good sense of humor.
    
    After considering that, asnwer the newest user input:
    {user_input}
    """
    
    if user_input == "q" or user_input == "quit":
        program_on = False
        break # Exit the loop immediately
    
    try:
        
        # ANIMATION while WATING for RESPONSE

        stop_spinner = False
        spinner_thread = threading.Thread(target=spinner, args=(lambda: stop_spinner,))
        spinner_thread.start()
        
        # GENERATE RESPONSE
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config
        )   
        
        # END OF ANIMATION while WATING for RESPONSE
        stop_spinner = True
        spinner_thread.join()   
        sys.stdout.write('\r')  # Move cursor to the beginning of the line
        sys.stdout.write(' ' * 10)  # Clear the line
        sys.stdout.write('\r')  # Move cursor back to the beginning
        sys.stdout.flush()
        
        # PRINT RESPONSE
        markdown_text: str | None = response.text
        markdown = Markdown(markdown_text) # type: ignore
        console.print(Panel(markdown, title="Gemini response", border_style="green"))
        print("\n" * 3)
        
        # COPY RESPONSE TO CLIPBOARD
        pyperclip.copy(markdown_text)
        print("[bold green]Response copied to clipboard[/bold green]")
        time.sleep(2)
        sys.stdout.write('\033[F ')  # Move cursor up 1 line
        
        CONVERSATION += f"""
## 🧑‍💻 User:
#### {user_input}

---
## 🤖 LLM:
{response.text}

---"""
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}") # Color-code error messages.)

save_conversation(CONVERSATION)

print("[bold magenta]Bye Bye[/bold magenta]") # Use color for the exit message.

      