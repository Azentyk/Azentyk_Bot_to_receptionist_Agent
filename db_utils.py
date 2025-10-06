from typing import Optional, List, Dict
from datetime import datetime
import hashlib
import pandas as pd
from pymongo import MongoClient
import logging
from typing import Optional, List, Dict,Tuple

# Initialize MongoDB client
url = r"mongodb://azentyk-doctor-appointment-app-server:ROtcf6VzE2Jj2Etn0D3QY9LbrSTs4MEgld2hynMw3R46gl8cuL1D70qvx4DjQvogoyBDVO2z1MJxACDb04M0BA==@azentyk-doctor-appointment-app-server.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@azentyk-doctor-appointment-app-server@"
client = MongoClient(url)
# client = MongoClient("mongodb+srv://azentyk:azentyk123@cluster0.b9aaq47.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
_db = client["patient_db"]
_collection = _db["patient_information_details_table"]


def get_pending_patient_information_data_from_db():
    return list(
        {
            "_id": str(doc.get("_id")),
            "username": doc.get("username"),
            "appointment_id": doc.get("appointment_id"),
            "hospital_name": doc.get("hospital_name"),
            "location": doc.get("location"),
            "specialization": doc.get("specialization"),
            "appointment_booking_date": doc.get("appointment_booking_date"),
            "appointment_booking_time": doc.get("appointment_booking_time"),
            "appointment_status": doc.get("appointment_status"),
        }
        for doc in _collection.find({"appointment_status": "Pending"})
    )


def update_appointment_status(appointment_id: str, new_status: str, new_date: str = None, new_time: str = None) -> dict:
    """
    Update appointment details in MongoDB.
    
    - For booking/cancel: only updates appointment_status
    - For reschedule: updates appointment_status + date + time
    - For confirmed/cancelled: updates appointment_status with clear messages

    Args:
        appointment_id (str): The appointment ID to match
        new_status (str): The new status ("booking in progress", "confirmed", "pending", "rescheduled", "cancelled")
        new_date (str, optional): The new appointment date (required if rescheduling)
        new_time (str, optional): The new appointment time (required if rescheduling)

    Returns:
        dict: A summary of the update result
    """

    update_fields = {"appointment_status": new_status.lower()}

    # Handle reschedule
    if new_status.lower() == "rescheduled":
        if not new_date or not new_time:
            return {
                "success": False,
                "message": "Reschedule requires both date and time."
            }
        update_fields["appointment_booking_date"] = new_date
        update_fields["appointment_booking_time"] = new_time

    # Perform MongoDB update
    result = _collection.update_one(
        {"appointment_id": appointment_id},
        {"$set": update_fields}
    )

    # Prepare response
    if result.modified_count > 0:
        # Custom messages for specific statuses
        if new_status.lower() == "rescheduled":
            message = f"Appointment {appointment_id} successfully rescheduled to {new_date} at {new_time}."
        elif new_status.lower() == "confirmed":
            message = f"Appointment {appointment_id} has been confirmed successfully."
        elif new_status.lower() == "cancelled":
            message = f"Appointment {appointment_id} has been cancelled successfully."
        else:
            message = f"Appointment {appointment_id} updated to status '{new_status}'."

        return {"success": True, "message": message}

    elif result.matched_count > 0:
        # Record found but no changes made
        return {
            "success": False,
            "message": f"Appointment {appointment_id} already has status '{new_status}'."
        }

    else:
        # No matching appointment found
        return {
            "success": False,
            "message": f"No appointment found with ID {appointment_id}."
        }
