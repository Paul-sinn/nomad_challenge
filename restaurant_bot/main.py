import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import Runner, SQLiteSession, function_tool, RunContextWrapper, InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered, MaxTurnsExceeded
from models import UserAccountContext

from my_agents.triage_agent import triage_agent




client = OpenAI()

user_account_ctx = UserAccountContext(
    customer_id=1,
    name="paul",
    tier="basic",
    email="unknown@example.com" ,
)


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]

async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\\$"))


asyncio.run(paint_history())


async def run_agent(message):

    with st.chat_message("assistant"):
        text_placeholder = st.empty()
        response = ""
        current_agent = triage_agent

        st.session_state["text_placeholder"] = text_placeholder
        
        try:

            stream = Runner.run_streamed(
                triage_agent,
                message,
                session=session,
                context=user_account_ctx,
                max_turns=3,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\\$"))

                elif event.type == "agent_updated_stream_event":
                    if current_agent.name != event.new_agent.name:
                        st.write(f"🤖 Transfered from {current_agent.name} to {event.new_agent.name}")
                        current_agent = event.new_agent

                        text_placeholder = st.empty()
                        response = ""
        except InputGuardrailTripwireTriggered:
            st.write("I can't help you with that.. Sorry")
        
        except OutputGuardrailTripwireTriggered:
            st.write ("Sorry, this agent can not help with that. Maybe other agent can help with that")
            st.session_state["text_placeholder"].empty()

        except MaxTurnsExceeded:
            st.write("I'm having trouble routing this request. Could you clarify whether this is about menu, ordering, or reservation?")

         


message = st.chat_input(
    "Write a message for your assistant",
)

if message:
    with st.chat_message("user"):
        st.write(message)
    asyncio.run(run_agent(message))


with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
