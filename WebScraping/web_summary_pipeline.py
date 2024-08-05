# web_summary_pipeline.py

import re
from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel
import sys
import subprocess
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from openai import AsyncOpenAI

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("requests")
install("playwright")
install("beautifulsoup4")
install("openai")

subprocess.run(["playwright", "install"], check=True)
subprocess.run(["playwright", "install-deps"], check=True)

def extract_urls(text):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return list(set(re.findall(url_pattern, text)))

async def setup_playwright():
    try:
        async with async_playwright() as p:
            await p.chromium.install()
    except Exception as e:
        print(f"Error setting up Playwright: {e}")

def filter_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    main_content = soup.select_one('main, #content, .main-content, article')
    text = main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()[:1000]
    return ' '.join(words)

def extract_dates(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b',
        r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, soup.get_text()))
    return list(set(dates))

def create_prompt(urls, topics, max_tokens):
    topics_str = ", ".join(topics)
    prompt = (
        f"Please create concise summaries of the following web pages, unless they are 404 or similar failures. "
        f"For each summary:\n"
        f"- Start with the URL enclosed in brackets, like this: [URL]\n"
        f"- Follow these guidelines:\n"
        f"  - Start each summary with a hyphen followed by a space ('- ').\n"
        f"  - If bullet points are appropriate, use a tab followed by a hyphen and a space ('\\t- ') for each point.\n"
        f"  - Check the provided list of topics and include the most relevant ones inline within the summary.\n"
        f"  - Each relevant topic should be marked only once in the summary.\n"
        f"  - Use UK English spelling throughout.\n"
        f"  - If a web page is inaccessible, mention that instead of providing a summary.\n"
        f"- Keep each summary to approximately {max_tokens} tokens.\n\n"
        f"List of topics to consider: {topics_str}\n\n"
        f"Web pages to summarize:\n" + "\n".join(urls)
    )
    return prompt

async def scrape_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            content = await page.content()
            filtered_content = filter_content(content)
            dates = extract_dates(content)
            return filtered_content, dates
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None, []
        finally:
            await browser.close()

async def summarize_batch(client, urls, topics, max_tokens, model):
    scraped_contents_dates = await asyncio.gather(*[scrape_url(url) for url in urls])
    scraped_contents = [content for content, dates in scraped_contents_dates]
    all_dates = [dates for content, dates in scraped_contents_dates]
    prompt = create_prompt(urls, topics, max_tokens)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes web pages."},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "I understand. I'll summarize the web pages and highlight relevant topics as requested."},
        {"role": "user", "content": "Here are the contents of the web pages:\n\n" + "\n\n".join([f"[{url}]\n{content}" for url, content in zip(urls, scraped_contents) if content])}
    ]
    
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens * len(urls)
    )
    
    summaries = response.choices[0].message.content
    return summaries, all_dates

def post_process_summaries(summaries, topics):
    processed_summaries = []
    for summary in summaries.split("[http"):
        if not summary.strip():
            continue
        summary = "[http" + summary
        parts = summary.split("]", 1)
        if len(parts) < 2:
            url = "Unknown URL"
            content = summary.strip()
        else:
            url = parts[0][1:]
            content = parts[1].strip()
        
        for topic in topics:
            if topic.lower() in content.lower():
                content = re.sub(r'\b{}\b'.format(re.escape(topic)), r'[[{}]]'.format(topic), content, count=1, flags=re.IGNORECASE)
        
        processed_summaries.append(f"{url}\n{content}")
    
    return "\n\n".join(processed_summaries)

async def get_available_models(api_key):
    client = AsyncOpenAI(api_key=api_key)
    try:
        models = await client.models.list()
        return [model.id for model in models.data if model.id.startswith(("gpt-3.5", "gpt-4"))]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return ["gpt-3.5-turbo", "gpt-4"]

class Pipeline:
    class Valves(BaseModel):
        OPENAI_API_KEY: str = ""
        TOPICS: str = ""
        MAX_TOKENS: int = 2000
        BATCH_SIZE: int = 10
        MODEL: str = "gpt-3.5-turbo"

    def __init__(self):
        self.name = "Efficient Web Summary Pipeline"
        self.valves = self.Valves()
        self.available_models = []

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        await setup_playwright()
        self.available_models = await get_available_models(self.valves.OPENAI_API_KEY)
        self.valves.MODEL = self.available_models[0] if self.available_models else "gpt-3.5-turbo"

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")
        try:
            openai_key = self.valves.OPENAI_API_KEY
            topics = [topic.strip() for topic in self.valves.TOPICS.split(",")]
            max_tokens = self.valves.MAX_TOKENS
            batch_size = self.valves.BATCH_SIZE
            model = self.valves.MODEL
            
            urls = extract_urls(user_message)
            
            if not urls:
                return "No valid URLs found in the input text."
            
            client = AsyncOpenAI(api_key=openai_key)
            
            all_summaries = []
            
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i+batch_size]
                batch_summaries, dates = asyncio.run(summarize_batch(client, batch, topics, max_tokens, model))
                all_summaries.append(batch_summaries)
                print(f"Extracted dates: {dates}")
            
            combined_summaries = "\n".join(all_summaries)
            processed_summaries = post_process_summaries(combined_summaries, topics)
            
            return processed_summaries
        except Exception as e:
            print(f"Error in pipe function: {e}")
            return f"An error occurred while processing the request: {str(e)}"

    def get_config(self):
        return {
            "OPENAI_API_KEY": {"type": "string", "value": self.valves.OPENAI_API_KEY},
            "TOPICS": {"type": "string", "value": self.valves.TOPICS},
            "MAX_TOKENS": {"type": "number", "value": self.valves.MAX_TOKENS},
            "BATCH_SIZE": {"type": "number", "value": self.valves.BATCH_SIZE},
            "MODEL": {"type": "select", "value": self.valves.MODEL, "options": self.available_models}
        }
