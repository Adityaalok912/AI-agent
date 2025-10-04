from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from api.ai.llms import get_openai_llm, get_groq_llm

from api.ai.tools import (
    send_me_email,
    get_unread_emails,
    research_email
)

EMAIL_TOOLS_LIST = [
    send_me_email,
    get_unread_emails,
]


def get_email_agent():
    model = get_groq_llm()
    agent = create_react_agent(
        model=model,  
        tools=EMAIL_TOOLS_LIST,  
        prompt="You are a helpful assistant for managing my email inbox for generating, sending, and reviewing emails.",
        name="email_agent"
    )

    return agent


def get_research_agent():
    model = get_groq_llm()
    agent = create_react_agent(
        model=model,  
        tools=[research_email],
        prompt="You are a helpful research assistant for preparing email data",
        name='research_agent',
    )

    return agent

# supe = get_supervisor()
# supe.invoke({"messages": [{"role": "user", "content": "Find out how to create a latte then email me the results."}]})
def get_supervisor(checkpointer=None):
    llm = get_groq_llm()
    email_agent = get_email_agent()
    research_agent = get_research_agent()

    supe = create_supervisor(
        agents=[email_agent, research_agent],
        model = llm,
         prompt=(
           "You are a supervisor that manages two agents:\n"
            "1. 'email_agent' — handles email reading, writing, and sending.\n"
            "2. 'research_agent' — handles information gathering and research.\n\n"
            "Your job: decide which agent should handle the user’s request.\n"
            "You may use the 'research_email' tool if you specifically need to "
            "research and generate an email response.\n"
            "Otherwise, delegate tasks to the appropriate agent."
        ),
        tools=[research_email],
       
    ).compile( checkpointer=checkpointer)
    return supe