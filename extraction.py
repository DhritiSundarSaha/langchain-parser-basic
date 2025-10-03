
from typing import Optional

from models import Person
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables.base import RunnableSequence

def create_extraction_chain(llm: ChatGoogleGenerativeAI) -> RunnableSequence:
    parser = PydanticOutputParser(pydantic_object=Person)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a strict information extractor. Your primary goal is to extract contact "
            "details for a person based on the user's text. Return ONLY valid JSON that "
            "matches the requested schema. If a piece of information (name, age, email, phone) "
            "is not mentioned, you MUST omit the key or set it to a reasonable default "
            "(e.g., age 0, name 'Unknown'). Do not guess or invent information."
        )),
        ("human", (
            "Extract a Person (name, age, email?, phone?) from this text:\n\n"
            "{text}\n\n{format_instructions}"
        ))
    ])

    return prompt | llm | parser

def try_extract_person_from_text(text: str, chain: RunnableSequence) -> Optional[Person]:
    parser = PydanticOutputParser(pydantic_object=Person)
    try:
        return chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
    except Exception as e:
        print(f"Error during extraction: {e}")
        return None