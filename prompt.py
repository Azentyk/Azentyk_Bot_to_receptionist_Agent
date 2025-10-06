from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime

def doctor_appointment_patient_data_extraction_prompt(llm):
    DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT = """
    You are an intelligent assistant from Azentyk that helps users book and track doctor appointments.  
    Your task is to extract structured appointment details from the conversation history.

    Please read the entire conversation history below and extract the following fields based on the user’s responses:  
    - **username**  
    - **phone_number**  
    - **mail**  
    - **location**  
    - **hospital_name**  
    - **doctor name and spcialization name **  
    - **appointment_booking_date** (for the appointment date)  
    - **appointment_booking_time** (for the appointment time)  
    - **appointment_status** (should be either "booking in progress", "confirmed", "pending","cancelled", "rescheduled")

    If any information is missing or not mentioned, leave its value as `null`.

    Format your final response as a valid JSON object like below:
    ```json
    {{
    "username": "<user name here>",
    "phone_number": "<user phone here>",
    "mail": "<user email here>",
    "location": "<location here>",
    "hospital_name": "<hospital name here>",
    "specialization": "<doctor name and specialization name here>",
    "appointment_booking_date": "<booking appointment date here>",
    "appointment_booking_time": "<booking appointment time here>",
    "appointment_status": "<booking in progress | confirmed | pending |cancelled |rescheduled | null>"
    }}```

    ### **Conversation History:**  
    {conversation_history}  

    Now, based on the conversation above, generate a valid JSON object as the output.


    """

    prompt = ChatPromptTemplate.from_template(DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT)

    rag_chain = (prompt | llm | JsonOutputParser())

    return rag_chain


def doctor_appointment_patient_data_extraction__cancel_prompt(llm):
    DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT = """
    You are an intelligent assistant from Azentyk that helps users cancel and track doctor appointments.  
    Your task is to extract structured appointment details from the conversation history.

    Please read the entire conversation history below and extract the following fields:  
    - **username
    - **appointment_id**  
    - **appointment_status** (should be either "cancelled",  or `null`)

    If any information is missing or not mentioned, leave its value as `null`.

    Format your final response as a valid JSON object like below:
    ```json
    {{
    "username": "<patient name here>"
    "appointment_id": "<appointment id here>",
    "appointment_status": ""cancelled",  or `null`"
    }}```

    ### **Conversation History:**  
    {conversation_history}  

    Now, based on the conversation above, generate a valid JSON object as the output.
    """

    prompt = ChatPromptTemplate.from_template(DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT)

    rag_chain = (prompt | llm | JsonOutputParser())

    return rag_chain


# def doctor_appointment_patient_data_extraction__rescheduled_prompt(llm):
#     DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT = """
#     You are an intelligent assistant from Azentyk that helps users rescheduled and track doctor appointments.  
#     Your task is to extract structured appointment details from the conversation history.

#     Please read the entire conversation history below and extract the following fields:  
#     - **username
#     - **appointment_id**  
#     - **appointment_status** (should be either "rescheduled",  or `null`)

#     If any information is missing or not mentioned, leave its value as `null`.

#     Format your final response as a valid JSON object like below:
#     ```json
#     {{
#     "username": "<patient name here>"
#     "appointment_id": "<appointment id here>",
#     "appointment_status": ""rescheduled",  or `null`"
#     }}```

#     ### **Conversation History:**  
#     {conversation_history}  

#     Now, based on the conversation above, generate a valid JSON object as the output.
#     """

#     prompt = ChatPromptTemplate.from_template(DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT)

#     rag_chain = (prompt | llm | JsonOutputParser())

#     return rag_chain


def doctor_appointment_patient_data_extraction__rescheduled_prompt(llm):
    DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT = """
    You are an intelligent assistant from Azentyk that helps users reschedule and track doctor appointments.  
    Your task is to extract structured appointment details from the conversation history.

    Current Year : 2025 

    Please read the entire conversation history below and extract the following fields:  
    - **username**  
    - **appointment_id**  
    - **appointment_status** (should be either "rescheduled" or `null`)  
    - **new_date** (the new appointment date if mentioned, otherwise `null`)  
    - **new_time** (the new appointment time if mentioned, otherwise `null`)  

    If any information is missing or not mentioned, leave its value as `null`.

    Format your final response as a valid JSON object like below:
    ```json
    {{
        "username": "<patient name here>",
        "appointment_id": "<appointment id here>",
        "appointment_status": "rescheduled" or null,
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



def bot_receptionist_doctor_appointment_patient_data_extraction(llm):
    DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT = """
    You are an intelligent assistant from Azentyk Doctor Appointment.  
    Your task is to extract structured appointment details from the conversation history.

    Please read the entire conversation history below and extract the following fields:  
    - **username
    - **appointment_id**  
    - **appointment_status** (should be either "confirmed", "cancelled", "rescheduled" ,  or `null`)

    If any information is missing or not mentioned, leave its value as `null`.

    Format your final response as a valid JSON object like below:
    ```json
    {{
    "username": "<patient name here>"
    "appointment_id": "<appointment id here>",
    "appointment_status": ""<appointment status here>"
    }}```

    ### **Conversation History:**  
    {conversation_history}  

    Now, based on the conversation above, generate a valid JSON object as the output.
    """

    prompt = ChatPromptTemplate.from_template(DOCTOR_APPOINTMENT_PATIENT_DATA_EXTRACTION_PROMPT)

    rag_chain = (prompt | llm | JsonOutputParser())

    return rag_chain

