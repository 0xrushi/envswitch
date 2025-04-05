import json
import re
from typing import List, Tuple, Optional
from difflib import ndiff
from thefuzz import fuzz
from rich.console import Console
from rich.syntax import Syntax
from openai import OpenAI
import os
import openai

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()

class EnvSwitchAgent:
    def __init__(self, file_path: str, context_path: str, intent: str):
        self.file_path = file_path
        self.context_path = context_path
        self.intent = intent.lower()
        self.context_map = self._load_context()
        self.file_text = self._load_file_text()
        self.current_env = None
        self.target_env = None
        self.replacements = []
        self.updated_text = ""
        self.total_tokens = 0

    def _load_file_text(self) -> str:
        with open(self.file_path, "r") as f:
            return f.read()

    def _load_context(self) -> dict:
        with open(self.context_path, "r") as f:
            return json.load(f)

    def _fuzzy_find(self, value: str, text: str, threshold: int = 85) -> Optional[str]:
        for line in text.splitlines():
            tokens = re.findall(r'"[^"]+"|\S+', line)
            for token in tokens:
                token_clean = token.strip('"')
                if fuzz.ratio(token_clean, value) >= threshold:
                    return token_clean
        return None

    def _detect_current_env(self) -> Optional[str]:
        scores = {}
        for env, values in self.context_map.items():
            scores[env] = sum(1 for key in values if key in self.file_text)

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else None

    def query_llm_for_env(self, intent: str) -> Optional[str]:
        system_prompt = "You are a helpful assistant that maps user instructions to environment names."

        user_prompt = f"""
        User instruction: "{intent}"
        Available environments: {list(self.context_map.keys())}

        Respond with just one of the environment names from the list above. If they dont match, respond None.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            self.total_tokens += response.usage.total_tokens
            console.print(f"[blue]ℹ Token usage: {response.usage.total_tokens}[/blue]")
            result = response.choices[0].message.content.strip()
            if result in self.context_map:
                return result
            else:
                console.print(f"[red]⚠️ LLM returned unknown environment: {result}[/red]")
                return None
        except Exception as e:
            console.print(f"[red]❌ LLM intent resolution failed: {e}[/red]")
            return None
    
    def query_llm_for_file_edit(self, intent: str) -> Optional[str]:
        system_prompt = (
            "You are a precise file editing agent.\n"
            "Given a user instruction and the full file content, return the updated file.\n"
            "Do not explain anything. Just return the modified file content as plain text."
        )

        user_prompt = f"""
    User instruction:
    {intent}

    Original file:
    {self.file_text}
    """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            self.total_tokens += response.usage.total_tokens
            return response.choices[0].message.content.strip()

        except Exception as e:
            console.print(f"[red]❌ LLM file-edit failed: {e}[/red]")
            return None


    def _apply_replacements(self):
        cur_map = self.context_map[self.current_env]
        tgt_map = self.context_map[self.target_env]
        self.updated_text = self.file_text

        for old_val, label in cur_map.items():
            new_val = next((k for k, v in tgt_map.items() if v == label), None)
            if not new_val or old_val == new_val:
                continue

            if old_val in self.updated_text:
                self.updated_text = self.updated_text.replace(old_val, new_val)
                self.replacements.append((old_val, new_val))
            else:
                fuzzy_match = self._fuzzy_find(old_val, self.updated_text)
                if fuzzy_match and fuzzy_match != new_val:
                    self.updated_text = self.updated_text.replace(fuzzy_match, new_val)
                    self.replacements.append((fuzzy_match, new_val))


    def process_environment_switch(self) -> bool:
        console.print(f"\n[bold yellow]🧠 Intent:[/bold yellow] {self.intent}")
        
        self.target_env = self.query_llm_for_env(self.intent)
        
        if self.target_env:
            self.current_env = self._detect_current_env()
            if not self.current_env:
                console.print("[red]Could not detect current environment from file.[/red]")
                return False
            self._apply_replacements()
            console.print(f"\n[bold yellow]🔄 Detected environment:[/bold yellow] {self.current_env}")
            console.print(f"[bold green]➡ Switching to:[/bold green] {self.target_env}\n")
        else:
            # General agentic edit mode if environment not recognized
            edited = self.query_llm_for_file_edit(self.intent)
            if edited and edited != self.file_text:
                self.updated_text = edited
                self.replacements.append(("FULL FILE", "LLM Edit"))
                console.print("[green]✅ File edited using LLM based on intent.[/green]")
                return True
            else:
                console.print("[yellow]⚠️ No changes made. LLM returned same content or failed.[/yellow]")
                return False
        return True

    def run(self, summary=True, write=False):
        console.print("[cyan]🤖 Starting EnvSwitchAgent[/cyan]")
        
        if self.process_environment_switch():
            console.print(f"[blue]🔢 Total tokens used: {self.total_tokens}[/blue]")
            if summary:
                self.show_diff()
            if write:
                self.save()

    def save(self):
        with open(self.file_path, "w") as f:
            f.write(self.updated_text)
        console.print("\n[bold green]✅ Changes written to file.[/bold green]")

    def show_diff(self):
        console.print("\n[bold blue]🧪 Summary — showing diff:[/bold blue]")
        diff = ndiff(self.file_text.splitlines(keepends=True), self.updated_text.splitlines(keepends=True))
        for line in diff:
            if line.startswith('+'):
                console.print(f"[green]{line}[/green]", end='')
            elif line.startswith('-'):
                console.print(f"[red]{line}[/red]", end='')
            else:
                console.print(line, end='')