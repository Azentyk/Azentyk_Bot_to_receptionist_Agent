from model import llm_model
from retriever import retriever_model
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
import shutil
import uuid
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

llm = llm_model()
retriever = retriever_model()

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


def get_pending_patient_information_data_from_db():
    from pymongo import MongoClient

    # Connect to MongoDB (Default Port: 27017)
    url = r"mongodb://azentyk-doctor-appointment-app-server:ROtcf6VzE2Jj2Etn0D3QY9LbrSTs4MEgld2hynMw3R46gl8cuL1D70qvx4DjQvogoyBDVO2z1MJxACDb04M0BA==@azentyk-doctor-appointment-app-server.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@azentyk-doctor-appointment-app-server@"
    client = MongoClient(url)

    # Create a database
    db = client["patient_db"]

    # Access the collection (table)
    patient_information_details_table_collection = db["patient_information_details_table"]

    # Create a list to store extracted data
    result_list = []

    # Filter for only documents where appointment_status is "Pending"
    query = {"appointment_status": "Pending"}

    # Loop through filtered documents and extract desired keys
    for document in patient_information_details_table_collection.find(query):
        data = {
            "username": document.get("username"),
            "hospital_name": document.get("hospital_name"),
            "location": document.get("location"),
            "specialization": document.get("specialization"),
            "appointment_booking_date": document.get("appointment_booking_date"),
            "appointment_booking_time": document.get("appointment_booking_time"),
            "appointment_status": document.get("appointment_status"),
        }
        result_list.append(data)

    return result_list


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("patient_data", None)
            current_date = configuration.get("current_date", None)
            state = {**state, "user_info": passenger_id,"current_date": current_date}
            # print("state: ")
            # print(state)
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        # print({"messages": result})
        return {"messages": result}
    

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """

You are Azentyk AI Doctor Assistant — a polite, professional, and friendly virtual assistant that helps hospitals schedule doctor appointments on behalf of patients. You are simulating a phone call conversation with hospital receptionists.

### 🎯 Core Goal
Your only role is to schedule, reschedule, or cancel doctor appointments by interacting with the receptionist in natural conversational style.

### 📞 Conversation Rules
- Always sound like a polite human caller (not a chatbot).
- Always follow the step-by-step call flow strictly.
- Only speak one step per turn.
- Always end your response with <END_OF_TURN>.
- End the entire call with <END_OF_CALL> plus a JSON status.
- Never merge multiple steps into one turn.
- Keep sentences short, clear, and natural.
- Never use bullet points in actual call responses (they are only in this instruction).

### 📞 Conversation Flow

**Step 1 – Greeting (always first line in every call)**
- Hello, this is Azentyk AI Doctor Assistant. I’m calling to help schedule an appointment for {{patientname}}. <END_OF_TURN>

**Step 2 – Appointment Request**
- The patient {{patientname}} would like to see Dr. {{doctor_name}} at {{hospital_name}}, {{location}} on {{appointment_date}} at {{appointment_time}}. Could you confirm if that slot is available? <END_OF_TURN>

**Step 3A – If Slot Is Available**
- Thank you. I’ll update the patient with the confirmed details.
    ```json
    {{ "appointment_status": "confirmed" }}
    ```
    <END_OF_CALL>

**Step 3B – If Slot Is Not Available**
- I understand. Could you share the alternative available dates and times for Dr. {{doctor_name}}? <END_OF_TURN>

**Step 4 – Clarification When Alternatives Are Shared**
- If receptionist gives only a date → “Got it. Could you tell me the available time for that date?” <END_OF_TURN>
- If receptionist gives only a time → “Thanks. Could you confirm the date for that time?” <END_OF_TURN>
- If receptionist gives both date and time → “Thank you. Could you confirm that I should proceed with booking {{appointment_date}} at {{appointment_time}}?” <END_OF_TURN>

**Step 5 – Confirm Rescheduled Appointment**
- Perfect. I’ll update the patient with the rescheduled details.  
    ```json
    {{ "appointment_status": "rescheduled" }}
    ```
    <END_OF_CALL>

**Step 6. If Appointment Is Cancelled**  
- Got it. I’ll update the patient accordingly.  
    ```json
    {{ "appointment_status": "cancelled" }}
    ```
    <END_OF_CALL>

### **If Receptionist Asks for Appointment Details:**
- Provide full info naturally, example:
“The patient’s name is {{patientname}}. The appointment is for {{hospital_name}}, located in {{location}}.” <END_OF_TURN>

### **If Receptionist Asks About Non-Appointment Topics:**
- Politely decline, example:
“I’m only here to help with doctor appointment scheduling, rescheduling, or cancellations. For other queries, please contact the hospital directly.” <END_OF_TURN>

**Context**:

Current Patient Info:
<User>
{user_info}
</User>

Current Date:
<Date>
{current_date}
</Date>

"""
        ),
        ("placeholder", "{messages}"),
    ]
)



from langchain.tools import tool

@tool
def google_search_hospital_details(query: str) -> str:
    """Search for hospital information including:
    - Hospital names
    - Hospital locations
    - Available specialties
    
    Use this when users ask about hospital options, specialties, etc.
    
    Use this tool only if no answer from hospital_details db"""
    docs = retriever.invoke(" ")
    return ""


part_1_tools = [google_search_hospital_details]
part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition

builder = StateGraph(State)


# Define nodes: these do the work
builder.add_node("assistant", Assistant(part_1_assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(part_1_tools))
# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
part_1_graph = builder.compile(checkpointer=memory)
