import asyncio

from agent_sandbox import Sandbox
from browser_use import Agent, Tools
from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI

sandbox = Sandbox(base_url="http://localhost:8080")
print("sandbox", sandbox.browser)
cdp_url = sandbox.browser.get_info().data.cdp_url

browser_session = BrowserSession(
    browser_profile=BrowserProfile(cdp_url=cdp_url, is_local=True)
)
tools = Tools()


async def main():
    agent = Agent(
        task='Visit https://duckduckgo.com and search for "browser-use founders"',
        llm=ChatOpenAI(model="gcp-claude4.1-opus"),
        tools=tools,
        browser_session=browser_session,
    )

    await agent.run()
    await browser_session.kill()

    input("Press Enter to close...")


if __name__ == "__main__":
    asyncio.run(main())
