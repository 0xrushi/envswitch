#!/usr/bin/env python3

import typer
from .agent import EnvSwitchAgent
from rich.console import Console

app = typer.Typer(
    name="envswitch",
    help="A CLI tool to switch environment configurations in files"
)
console = Console()

@app.command()
def switch(
    file: str = typer.Argument(..., help="Path to input file"),
    context: str = typer.Argument(..., help="Path to context JSON"),
    intent: str = typer.Argument(..., help="Instruction (e.g. 'convert to staging')"),
    write: bool = typer.Option(False, "-w", "--write", help="Write changes to file"),
    summary: bool = typer.Option(True, "--summary", help="Preview only"),
):
    """
    Switch environment configurations in a file based on context and intent.
    """
    try:
        agent = EnvSwitchAgent(file, context, intent)
        agent.run(summary=summary, write=write)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

def main():
    app()

if __name__ == "__main__":
    main()