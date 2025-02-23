import webbrowser
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown


def open_website(url: str) -> None:
    """Opens a website in the default browser."""
    webbrowser.open_new_tab(url)


def main():
    console = Console()

    # Define your website options
    website_options = {
        "Google": "https://www.google.com",
        "YouTube": "https://www.youtube.com",
        "Stack Overflow": "https://stackoverflow.com",
        "GitHub": "https://github.com"
    }

    # Use rich to display the options in a fancy panel
    markdown_text = "\n".join(f"- {site}" for site in website_options.keys())
    markdown = Markdown(markdown_text)
    panel = Panel(
        markdown, title="[b]Available Websites[/b]", border_style="blue")
    console.print(panel)

    # Get user selection using rich prompt
    while True:
        selection = Prompt.ask(
            "Choose a website to open (or type 'exit' to quit)", choices=[
                               *website_options.keys(), "exit"]
                               )
        if selection == "exit":
            console.print("Exiting... Goodbye!")
            break
        elif selection in website_options:
            url = website_options[selection]
            console.print(f"Opening [link={url}]{selection}[/link]...")
            open_website(url)
        else:
            console.print(
                "[red]Invalid selection. Please choose from the list.[/red]")


if __name__ == "__main__":
    main()
