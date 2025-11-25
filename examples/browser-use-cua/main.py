import asyncio
import os
from typing import TYPE_CHECKING
from dotenv import load_dotenv
from browser_use import Agent, Tools
from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI
from browser_use.agent.views import ActionResult

import asyncio
import base64
import os
from io import BytesIO

from agent_sandbox import Sandbox
from agent_sandbox.browser.types.action import (
    Action_Click,
    Action_DoubleClick,
    Action_DragTo,
    Action_MoveTo,
    Action_Press,
    Action_Scroll,
    Action_Typing,
    Action_Wait,
)
from PIL import Image
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from openai.types.responses import ComputerAction

# Load environment variables from .env file
load_dotenv()

sandbox_url = os.getenv("SANDBOX_BASE_URL", "http://localhost:8080")
sandbox = Sandbox(base_url=sandbox_url)
cdp_url = sandbox.browser.get_info().data.cdp_url

browser_session = BrowserSession(
    browser_profile=BrowserProfile(cdp_url=cdp_url, is_local=True)
)
tools = Tools()


class SandboxGUIAction(BaseModel):
    """Parameters for Sandbox GUI action (CUA-style fallback)."""

    description: str = Field(..., description="Description of your next goal")


async def take_screenshot() -> str | None:
    """Take a screenshot from sandbox and return as base64 string."""
    try:
        screenshot_bytes = b""
        async for chunk in sandbox.browser.screenshot():
            screenshot_bytes += chunk

        if not screenshot_bytes:
            return None

        return base64.b64encode(screenshot_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None


async def handle_cua_action(action: "ComputerAction") -> ActionResult:
    """
    Map OpenAI CUA action to sandbox execute_action API.
    This bridges the CUA response format to our sandbox's action types.
    """
    action_type = action.type
    ERROR_MSG: str = "Could not execute the GUI action."

    try:
        match action_type:
            case "click":
                x, y = action.x, action.y
                button = action.button

                print(f"Action: click at ({x}, {y}) with button '{button}'")

                # Map CUA button to sandbox button
                from agent_sandbox.browser.types.action import Button

                button_map = {
                    "left": Button.LEFT,
                    "right": Button.RIGHT,
                    "middle": Button.MIDDLE,
                }
                sandbox_button = button_map.get(button, Button.LEFT)

                await sandbox.browser.execute_action(
                    request=Action_Click(
                        action_type="CLICK",
                        x=float(x),
                        y=float(y),
                        button=sandbox_button,
                        num_clicks=1,
                    )
                )

                msg = f"Clicked at ({x}, {y}) with button {button}"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "double_click":
                x, y = action.x, action.y
                print(f"Action: double click at ({x}, {y})")

                await sandbox.browser.execute_action(
                    request=Action_DoubleClick(
                        action_type="DOUBLE_CLICK",
                        x=float(x),
                        y=float(y),
                    )
                )

                msg = f"Double clicked at ({x}, {y})"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "scroll":
                x, y = action.x, action.y
                scroll_x, scroll_y = action.scroll_x, action.scroll_y
                print(
                    f"Action: scroll at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})"
                )

                # First move to position
                await sandbox.browser.execute_action(
                    request=Action_MoveTo(
                        action_type="MOVE_TO",
                        x=float(x),
                        y=float(y),
                    )
                )

                # Then scroll
                await sandbox.browser.execute_action(
                    request=Action_Scroll(
                        action_type="SCROLL",
                        dx=int(scroll_x) if scroll_x else 0,
                        dy=int(scroll_y) if scroll_y else 0,
                    )
                )

                msg = f"Scrolled at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "keypress":
                keys = action.keys
                print(f"Action: keypress '{keys}'")

                for key in keys:
                    # Map common key names
                    key_map = {
                        "enter": "Return",
                        "space": "space",
                        "tab": "Tab",
                        "escape": "Escape",
                        "backspace": "BackSpace",
                        "delete": "Delete",
                    }
                    mapped_key = key_map.get(key.lower(), key)

                    await sandbox.browser.execute_action(
                        request=Action_Press(
                            action_type="PRESS",
                            key=mapped_key,
                        )
                    )

                msg = f"Pressed keys: {keys}"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "type":
                text = action.text
                print(f"Action: type text: {text}")

                await sandbox.browser.execute_action(
                    request=Action_Typing(
                        action_type="TYPING",
                        text=text,
                        use_clipboard=False,
                    )
                )

                msg = f"Typed text: {text}"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "drag":
                # CUA drag action: drag from current position or specified start to end
                start_x = getattr(action, "start_x", None)
                start_y = getattr(action, "start_y", None)
                end_x = action.x
                end_y = action.y

                print(f"Action: drag from ({start_x}, {start_y}) to ({end_x}, {end_y})")

                if start_x is not None and start_y is not None:
                    # Move to start position first
                    await sandbox.browser.execute_action(
                        request=Action_MoveTo(
                            action_type="MOVE_TO",
                            x=float(start_x),
                            y=float(start_y),
                        )
                    )

                # Execute drag to target
                await sandbox.browser.execute_action(
                    request=Action_DragTo(
                        action_type="DRAG_TO",
                        x=float(end_x),
                        y=float(end_y),
                    )
                )

                msg = f"Dragged to ({end_x}, {end_y})"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "wait":
                print("Action: wait")
                await sandbox.browser.execute_action(
                    request=Action_Wait(
                        action_type="WAIT",
                        duration=2.0,
                    )
                )
                msg = "Waited for 2 seconds"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case "screenshot":
                # Screenshot is automatically taken, no action needed
                print("Action: screenshot (already taken)")
                return ActionResult(
                    extracted_content="Screenshot captured",
                    include_in_memory=True,
                )

            case "move":
                x, y = action.x, action.y
                print(f"Action: move to ({x}, {y})")

                await sandbox.browser.execute_action(
                    request=Action_MoveTo(
                        action_type="MOVE_TO",
                        x=float(x),
                        y=float(y),
                    )
                )

                msg = f"Moved mouse to ({x}, {y})"
                return ActionResult(
                    extracted_content=msg, include_in_memory=True, long_term_memory=msg
                )

            case _:
                print(f"Unrecognized action type: {action_type}")
                return ActionResult(error=ERROR_MSG)

    except Exception as e:
        print(f"Error handling action {action}: {e}")
        return ActionResult(error=f"{ERROR_MSG}: {e}")


tools = Tools()


@tools.registry.action(
    "Use Sandbox GUI as a fallback when standard browser actions cannot achieve the desired goal. "
    "This action takes a screenshot and uses OpenAI CUA to determine the next GUI action, "
    "then executes it via the sandbox browser API.",
    param_model=SandboxGUIAction,
)
async def sandbox_gui_fallback(
    params: SandboxGUIAction
) -> ActionResult:
    """
    Fallback action that uses OpenAI's CUA to analyze screenshots and perform
    complex GUI interactions via the sandbox browser API.
    """

    print(f"GUI Action Starting - Goal: {params.description}")

    try:
        # Get browser info for viewport dimensions
        browser_info = await sandbox.browser.get_info()
        viewport_width = browser_info.data.width or 1920
        viewport_height = browser_info.data.height or 1080

        print(f"Viewport size: {viewport_width}x{viewport_height}")

        # Take screenshot from sandbox
        screenshot_b64 = await take_screenshot()
        if not screenshot_b64:
            return ActionResult(error="Failed to take screenshot from sandbox")

        print(f"Screenshot captured (base64 length: {len(screenshot_b64)} chars)")

        # Check and resize screenshot to match viewport
        image = Image.open(BytesIO(base64.b64decode(screenshot_b64)))
        print(f"Screenshot actual dimensions: {image.size[0]}x{image.size[1]}")

        if image.size != (viewport_width, viewport_height):
            image = image.resize((viewport_width, viewport_height))
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            screenshot_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            print(f"Rescaled screenshot to viewport size: {viewport_width}x{viewport_height}")

        # Use OpenAI CUA to determine the action
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("Sending request to OpenAI CUA...")

        prompt = f"""
        You will be given an action to execute and screenshot of the current screen.
        Output one computer_call object that will achieve this goal.
        Goal: {params.description}
        """

        response = await client.responses.create(
            model="computer-use-preview",
            tools=[
                {
                    "type": "computer_use_preview",
                    "display_width": viewport_width,
                    "display_height": viewport_height,
                    "environment": "browser",
                }
            ],
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "detail": "auto",
                            "image_url": f"data:image/png;base64,{screenshot_b64}",
                        },
                    ],
                }
            ],
            truncation="auto",
            temperature=0.1,
        )

        print(f"CUA response received: {response}")

        # Extract computer call from response
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        computer_call = computer_calls[0] if computer_calls else None

        if not computer_call:
            return ActionResult(error="No computer calls found in CUA response")

        action = computer_call.action
        print(f"Executing CUA action: {action.type} - {action}")

        # Execute the action via sandbox API
        action_result = await handle_cua_action(action)
        await asyncio.sleep(0.1)

        print("GUI action completed successfully")
        return action_result

    except Exception as e:
        msg = f"Error executing GUI action: {e}"
        print(f"{msg}")
        return ActionResult(error=msg)


async def main():
    browser_session = BrowserSession(browser_profile=BrowserProfile(cdp_url=cdp_url))

    # Task that might require GUI fallback for complex interactions
    task = """
    Visit https://duckduckgo.com and search for "browser-use founders

    Note: If certain interactions cannot be completed using standard browser operations, the sandbox_gui_fallback tool can be used.
    Perform complex mouse/keyboard operations through GUI screenshot analysis.
    """

    agent = Agent(
        task=task,
        llm=ChatOpenAI(model=os.getenv("OPENAI_MODEL_ID", "gpt-5-2025-08-07")),
        use_vision=True,
        tools=tools,
        browser_session=browser_session,
    )

    print("Starting agent with Sandbox GUI fallback support...")
    print(f"Task: {task}")
    print("-" * 50)

    try:
        result = await agent.run()
        print(f"\nTask completed! Result: {result}")
    except Exception as e:
        print(f"\nError running agent: {e}")
    finally:
        await browser_session.kill()
        print("\nBrowser session closed")

    input("Press Enter to close...")


if __name__ == "__main__":
    print("Sandbox Browser Use with GUI Integration Example")
    print("=" * 60)
    print()
    print("This example shows how to integrate ByteDAI sandbox's browser API")
    print("(screenshot and execute_action) with browser-use, similar to CUA pattern.")
    print()
    print("The sandbox_gui_fallback tool is useful for:")
    print("  - Complex mouse interactions (drag & drop, precise clicking)")
    print("  - Keyboard shortcuts and key combinations")
    print("  - Actions that require pixel-perfect precision")
    print("  - Custom UI elements that don't respond to standard actions")
    print()

    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
