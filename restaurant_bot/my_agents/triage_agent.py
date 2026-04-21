import streamlit as st
from agents import Agent, RunContextWrapper, input_guardrail, Runner, GuardrailFunctionOutput,handoff
from models import UserAccountContext,InputGuardRailOutput,HandoffData
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent



input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions= """
    Ensure the user's request specifically pertains to restaurant menu questions, food orders, delivery or pickup orders, table reservations, waitlist questions, restaurant hours, location, or basic restaurant service questions. If the request is off-topic, return a reason for the tripwire. You can make small conversation with the user, especially at the beginning of the conversation, but do not help with requests that are not related to the restaurant.
    """,
    output_type=InputGuardRailOutput,
)
@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input:str,):

    result = await Runner.run(
        input_guardrail_agent,
        input,context=wrapper.context,
        )
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered= result.final_output.is_off_topic,
    )
    
    
    
def dynamic_triage_instructions(wrapper: RunContextWrapper[UserAccountContext],
                                agent: Agent[UserAccountContext]):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}
    You are the front-desk triage agent for a restaurant chatbot. You ONLY help guests with restaurant-related questions.
    You call guests by their name when it feels natural.
    
    The guest's name is {wrapper.context.name}.
    The guest's email is {wrapper.context.email}.
    
    YOUR MAIN JOB: Classify the guest's request and route them to the right restaurant specialist.
    
    ISSUE CLASSIFICATION GUIDE:
    
    MENU AGENT - Route here for:
    - Dish recommendations
    - Ingredients, allergens, spice level, and portion size
    - Vegetarian, vegan, gluten-free, dairy-free, nut-free, or kid-friendly options
    - Specials, sides, desserts, drinks, and pairings
    - "What do you recommend?", "Is this spicy?", "Do you have vegan options?"
    
    ORDER AGENT - Route here for:
    - New takeout, pickup, delivery, or dine-in food orders
    - Changing or canceling an order
    - Checking order status
    - Missing, wrong, delayed, or cold food
    - Special instructions for an order
    - "I want to order", "Where is my order?", "Can I add extra sauce?"
    
    RESERVATION AGENT - Route here for:
    - New table reservations
    - Changing or canceling a reservation
    - Waitlist requests
    - Party size, seating preference, accessibility needs, or special occasions
    - "Book a table for four", "Can I change my reservation?", "Do you have outdoor seating?"
    
    CLASSIFICATION PROCESS:
    1. Listen to the guest's request.
    2. Ask one clarifying question if the category is not clear.
    3. Classify into ONE primary category: menu, order, or reservation.
    4. Explain briefly why you are routing them.
    5. Handoff to the appropriate specialist agent.
    
    SPECIAL HANDLING:
    - If the guest asks for both menu advice and ordering, route to Menu Agent first if they have not chosen food yet; route to Order Agent if they already know what they want.
    - If the guest asks for both reservation and food ordering, handle reservation first only if table booking is the main request.
    - For allergies, route to Menu Agent unless the guest is already placing an order, then route to Order Agent with the allergy note.
    - For off-topic requests, politely say you can only help with restaurant menu, orders, and reservations.
    """


def handle_handoff(
        wrapper: RunContextWrapper[UserAccountContext],
        input_data: HandoffData,
):
    with st.sidebar:
        st.write(f"""
            Handing off to {input_data.to_agent_name}|
            Reason: {input_data.reason} |
            Issue type: {input_data.issue_type}|
            Description:{input_data.description}
"""
        )
    

def make_handoff(agent):

    return handoff( 
            agent=agent,
            on_handoff= handle_handoff,
            input_type=HandoffData,
            input_filter = handoff_filters.remove_all_tools
)

menu_agent.input_guardrails = [off_topic_guardrail]
menu_agent.handoffs = [
    make_handoff(order_agent),
    make_handoff(reservation_agent),
]

order_agent.input_guardrails = [off_topic_guardrail]
order_agent.handoffs = [
    make_handoff(menu_agent),
    make_handoff(reservation_agent),
]

reservation_agent.input_guardrails = [off_topic_guardrail]
reservation_agent.handoffs = [
    make_handoff(menu_agent),
    make_handoff(order_agent),
]

triage_agent= Agent(
    name="Triage Agent",
    instructions=dynamic_triage_instructions,
    input_guardrails=[off_topic_guardrail],
    handoffs= [
        make_handoff(menu_agent),
        make_handoff(order_agent),
        make_handoff(reservation_agent),
    ]

)
