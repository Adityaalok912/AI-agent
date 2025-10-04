from api.ai.llms import get_groq_llm
from api.ai.schemas import EmailMessageSchema


def generate_email_message(query:str) -> EmailMessageSchema:
    llm = get_groq_llm()
    llm = llm.with_structured_output(EmailMessageSchema)

    messages = [
        (
            "system", "You are a helpful assistant that helps people write better emails."
        ),
        (
            "human", f"{query}. Donot use markdown in your response only plain text."
        )
    ]

    return llm.invoke(messages)
   