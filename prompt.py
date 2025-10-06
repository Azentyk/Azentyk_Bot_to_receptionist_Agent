from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime


def bot_receptionist_doctor_appointment_patient_data_extraction(llm):
    DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT = """
    You are an intelligent assistant from Azentyk Doctor Appointment.  
    Your task is to extract structured appointment details from the conversation history.

    Current Year : 2025 

    Please read the entire conversation history below and extract the following fields:  
    - **username**  
    - **appointment_id**  
    - **appointment_status** (should be either "confirmed", "cancelled", "rescheduled" ,  or `null`)
    - **new_date** (the new appointment date if mentioned, otherwise `null`)  
    - **new_time** (the new appointment time if mentioned, otherwise `null`)  

    If any information is missing or not mentioned, leave its value as `null`.

    Format your final response as a valid JSON object like below:
    ```json
    {{
        "username": "<patient name here>",
        "appointment_id": "<appointment id here>",
        "appointment_status": "<appointment status here>",
        "new_date": "<DD-MM-YYYY or other format if user says, else null>",
        "new_time": "<HH:MM AM/PM or 24hr format, else null>"
    }}
    ```

    ### **Conversation History:**  
    {conversation_history}  

    Now, based on the conversation above, generate a valid JSON object as the output.
    """

    prompt = ChatPromptTemplate.from_template(DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT)

    rag_chain = (prompt | llm | JsonOutputParser())

    return rag_chain
