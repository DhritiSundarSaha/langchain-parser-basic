import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import Person

MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")
llm = ChatGoogleGenerativeAI(model=MODEL_ID)
parser = PydanticOutputParser(pydantic_object=Person)
format_instructions = parser.get_format_instructions()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict information extractor. Return ONLY valid JSON matching the schema."),
    ("human", """Extract a Person (name, age, email?, phone?) from this text:

{text}

Return ONLY valid JSON that matches the schema:
{format_instructions}
""")
])

extract_chain = prompt | llm | parser

def extract_person(text: str) -> Person:
    return extract_chain.invoke({"text": text, "format_instructions": format_instructions})
