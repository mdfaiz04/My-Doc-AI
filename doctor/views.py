from django.shortcuts import render
from django.conf import settings
import json
from ollama import Client
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from mydoc.db import users_col, doctors_col, appointments_col
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId
from datetime import datetime, date


# ---------------------------------------------------
# BASIC UI ROUTES
# ---------------------------------------------------

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def login(request):
    return render(request, 'login.html')

def chatbot(request):
    response_text = None

    if request.method == "POST":
        user_query = request.POST.get("patient_query", "").strip()

        if not user_query:
            response_text = "Please enter a question."
        else:
            try:
                client = Client(
                    host="https://ollama.com",
                    headers={"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}
                )

                messages = [
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": user_query},
                ]

                response_text = ""
                for part in client.chat("gpt-oss:120b", messages=messages, stream=True):
                    response_text += part["message"]["content"]

            except Exception as e:
                response_text = f"Error contacting Ollama Cloud: {e}"

    return render(request, "chatbot.html", {"response": response_text})


def json_req(request):
    try:
        return json.loads(request.body.decode())
    except:
        return {}


# ---------------------------------------------------
# DOCTOR LIST PAGE
# ---------------------------------------------------

def doctors(request):
    docs = list(doctors_col.find({}, {"password": 0}))
    for d in docs:
        d["_id"] = str(d["_id"])
    return render(request, "doctors.html", {"doctors": docs})


# ---------------------------------------------------
# USER LOGIN / REGISTER API
# ---------------------------------------------------

@csrf_exempt
def user_login_register_api(request):
    data = json_req(request)

    username_raw = data.get("username", "")
    password = data.get("password", "")
    register = data.get("register", False)

    username = username_raw.strip().lower()

    if not username or not password:
        return JsonResponse({"error": "username & password required"}, status=400)

    user = users_col.find_one({"username": username})

    # LOGIN
    if not register:
        if not user:
            return JsonResponse({"error": "user not found"}, status=404)

        if check_password(password, user["password"]):
            return JsonResponse({
                "msg": "login success",
                "role": user.get("role", "user"),
                "username": username
            })

        return JsonResponse({"error": "wrong password"}, status=400)

    # REGISTER
    if user:
        return JsonResponse({"error": "user already exists"}, status=400)

    users_col.insert_one({
        "username": username,
        "password": make_password(password),
        "role": "user"
    })

    return JsonResponse({
        "msg": "registered",
        "role": "user",
        "username": username
    })


# ---------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------

@csrf_exempt
def admin_login_api(request):
    data = json_req(request)

    admin_username = getattr(settings, "ADMIN_USERNAME", "admin")
    admin_password = getattr(settings, "ADMIN_PASSWORD", "admin123")

    if data.get("username") == admin_username and data.get("password") == admin_password:
        return JsonResponse({"msg": "admin login success"})

    return JsonResponse({"error": "invalid admin"}, status=400)


# ---------------------------------------------------
# ADMIN ADD DOCTOR
# ---------------------------------------------------

@csrf_exempt
def admin_add_doctor_api(request):
    data = json_req(request)

    admin_username = getattr(settings, "ADMIN_USERNAME", "admin")
    admin_password = getattr(settings, "ADMIN_PASSWORD", "admin123")

    if data.get("admin_user") != admin_username or data.get("admin_pass") != admin_password:
        return JsonResponse({"error": "unauthorized"}, status=403)

    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    name = data.get("name", username)
    specialization = data.get("specialization", "")

    if not username or not password:
        return JsonResponse({"error": "missing doctor info"}, status=400)

    doctors_col.insert_one({
        "username": username,
        "name": name,
        "password": username,   # default password
        "specialization": specialization,
        "designation": specialization,
        "work_days": "Mon-Sat"
    })

    return JsonResponse({"msg": "doctor added"})


# ---------------------------------------------------
# DOCTOR LOGIN
# ---------------------------------------------------

@csrf_exempt
def doctor_login_api(request):
    data = json_req(request)

    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip().lower()

    if not username or not password:
        return JsonResponse({"error": "missing fields"}, status=400)

    doctor = doctors_col.find_one({"username": username})

    if not doctor:
        return JsonResponse({"error": "doctor not found"}, status=404)

    if password != doctor["password"]:
        return JsonResponse({"error": "wrong password"}, status=400)

    return JsonResponse({
        "msg": "doctor login success",
        "role": "doctor",
        "doctor": username
    })


# ---------------------------------------------------
# BOOK APPOINTMENT
# ---------------------------------------------------

@csrf_exempt
def book_appointment_api(request):
    data = json_req(request)

    doctor_id = (data.get("doctor_id") or "").strip().lower()
    username = (data.get("username") or "").strip().lower()
    day = data.get("day", "")

    if not doctor_id or not username or not day:
        return JsonResponse({"error": "missing fields"}, status=400)

    if day < str(date.today()):
        return JsonResponse({"error": "Cannot select a past date"}, status=400)

    user = users_col.find_one({"username": username})
    if not user:
        return JsonResponse({"error": "user not found"}, status=404)

    # Fetch doctor by username
    doctor = doctors_col.find_one({"username": doctor_id})
    if not doctor:
        return JsonResponse({"error": "doctor not found"}, status=404)

    # Always store the doctor username
    doctor_username = doctor["username"]

    # Check slot
    exists = appointments_col.find_one({"doctor": doctor_username, "day": day})
    if exists:
        return JsonResponse({"error": "slot taken"}, status=409)

    # Create appointment
    appointments_col.insert_one({
        "doctor": doctor_username,
        "user": username,
        "day": day,
        "status": "Pending",
        "created_at": datetime.utcnow()
    })

    return JsonResponse({"msg": "appointment created", "status": "Pending"})



# ---------------------------------------------------
# DOCTOR APPOINTMENTS API
# ---------------------------------------------------

def doctor_appointments_api(request, doctor_name):
    doctor_name = doctor_name.strip().lower()

    appts = list(appointments_col.find({"doctor": doctor_name}))
    for a in appts:
        a["_id"] = str(a["_id"])

    return JsonResponse({"appointments": appts})


# ---------------------------------------------------
# UPDATE APPOINTMENT STATUS
# ---------------------------------------------------

@csrf_exempt
def update_appointment_api(request):
    data = json_req(request)
    appt_id = data.get("id")

    if not appt_id:
        return JsonResponse({"error": "missing id"}, status=400)

    new_status = "Approved" if data.get("action") == "approve" else "Rejected"

    appointments_col.update_one(
        {"_id": ObjectId(appt_id)},
        {"$set": {"status": new_status}}
    )

    return JsonResponse({"msg": f"Appointment {new_status}"})


# ---------------------------------------------------
# USER DASHBOARD (FIXED FOR DOCTOR DESIGNATION)
# ---------------------------------------------------

def user_dashboard(request):
    username = request.GET.get("user", "").strip().lower()

    # GET ALL DOCTORS
    doctors_list = list(doctors_col.find({}, {"password": 0}))
    for d in doctors_list:
        d["_id"] = str(d["_id"])

        # if designation missing, fallback to specialization
        if "designation" not in d:
            d["designation"] = d.get("specialization", "")

    # MAP → username → doctor details
    doctor_map = {d["username"]: d for d in doctors_list}

    # GET APPOINTMENTS FOR THIS USER
    appts = []
    if username:
        appts = list(appointments_col.find({"user": username}))
        for a in appts:
            a["_id"] = str(a["_id"])

            # Attach doctor details directly
            doctor_username = a.get("doctor")

            # Some old records may store full doctor name → fix automatically:
            if doctor_username not in doctor_map:
                for d in doctors_list:
                    if d["name"].lower() == doctor_username.lower():
                        doctor_username = d["username"]
                        break

            # Update appointment doctor field if repaired
            a["doctor"] = doctor_username

            # Attach full doctor details for template
            a["doc"] = doctor_map.get(doctor_username)

    today = date.today().isoformat()

    return render(request, "user_dashboard.html", {
        "doctors": doctors_list,
        "appointments": appts,
        "today": today,
    })



# ---------------------------------------------------
# DOCTOR DASHBOARD
# ---------------------------------------------------

def doctor_dashboard(request):
    return render(request, "doctor_dashboard.html")


# ---------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------

def admin_dashboard(request):
    doctors = list(doctors_col.find({}, {"password": 0}))
    users = list(users_col.find({}, {"password": 0}))

    doctor_stats = []
    for d in doctors:
        username = d["username"]
        count = appointments_col.count_documents({"doctor": username})
        doctor_stats.append({
            "name": d.get("name"),
            "username": username,
            "designation": d.get("designation"),
            "appointments": count
        })

    return render(request, "admin_dashboard.html", {
        "doctor_stats": doctor_stats,
        "users": users
    })


# ---------------------------------------------------
# GET ALL DOCTORS
# ---------------------------------------------------

def get_all_doctors(request):
    docs = list(doctors_col.find({}))
    for d in docs:
        d["_id"] = str(d["_id"])
        d.pop("password", None)

    return JsonResponse({"doctors": docs})
