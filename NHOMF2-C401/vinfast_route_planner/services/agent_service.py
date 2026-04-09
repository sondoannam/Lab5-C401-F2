import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from vinfast_route_planner.services.agent_tools import AGENT_TOOLS_SCHEMA, execute_tool

load_dotenv()

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "dummy_key_for_testing"),
)
_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-flash-1.5") # Using gemini-flash because it supports function calling better on openrouter, or openai

AGENT_SYSTEM_PROMPT = """
You are **VinFast AI Navigator**, an elite, production-ready EV Trip Planning Agent.
Your core objective is to assist users in planning electric vehicle (EV) routes, minimizing range anxiety, and ensuring strict safety constraints.

## System Capabilities (Tools)
You are equipped with function-calling capabilities. You must intelligently reason about WHEN and WHICH tool to call based on the user's intent. Do not hallucinate data—ask the user if essential parameters (e.g., Origin, Destination, or Current SoC) are missing.

## Operating Constraints
1. **Safety Buffer (Hard Constraint)**: The vehicle's State of Charge (SoC) MUST NEVER drop below `SoC_hard = 10%`. If you see arrive SoC < 10%, declare the route INFEASIBLE.
2. **Comfort Buffer**: Strive to keep SoC at or above the `SoC_comfort` threshold (default 20%). Raise a "Cảnh Báo Vàng" to the user if SoC falls between 10% and 19.9%.
3. **Mock Data Disclaimer**: Remind the user implicitly or explicitly occasionally that this is a mocked system.
4. **Tone & Language**: Always engage the user in a professional, clear, and empathetic **Vietnamese**. 

When generating your response, if you use a tool, explain what you found smoothly. Do not just output JSON.
"""

def chat_with_agent(messages: list) -> dict:
    """
    Executes a chat request with the ReAct agent, resolving tool calls if any.
    Returns the updated message history and any "workflow_data" if a route was planned.
    """
    
    # Prepend system prompt
    internal_msgs = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}] + messages
    
    workflow_data = None

    try:
        # Step 1: Call LLM
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=internal_msgs,
            tools=AGENT_TOOLS_SCHEMA,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        
        # Step 2: Check if LLM wants to call a tool
        if response_message.tool_calls:
            internal_msgs.append(response_message)
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                tool_result = execute_tool(func_name, func_args)
                
                # Check if it was a plan request to extract workflow_data
                if func_name == "plan_ev_route":
                    try:
                        parsed = json.loads(tool_result)
                        if "_raw_workflow_result" in parsed:
                            workflow_data = parsed.pop("_raw_workflow_result")
                            tool_result = json.dumps(parsed, ensure_ascii=False)
                    except:
                        pass
                
                # Append tool result to internal_msgs
                internal_msgs.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": tool_result
                })
                
            # Step 3: Get final response from LLM after tool calls
            final_response = _client.chat.completions.create(
                model=_MODEL,
                messages=internal_msgs
            )
            assistant_content = final_response.choices[0].message.content
        else:
            assistant_content = response_message.content

        return {
            "content": assistant_content,
            "workflow_data": workflow_data
        }
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            return {
                "content": "🔴 Lỗi xác thực (401): Hệ thống thiếu API Key của OpenRouter hoặc key không hợp lệ. Vui lòng cấu hình `OPENROUTER_API_KEY` trong file `.env` ở thư mục gốc của backend để sử dụng chức năng AI Agent nhé!",
                "workflow_data": None
            }
        return {
            "content": f"🔴 Lỗi hệ thống: {error_msg}",
            "workflow_data": None
        }
