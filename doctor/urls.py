from django.urls import path
from doctor import views

urlpatterns = [

    # --------------------
    # UI ROUTES
    # --------------------
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact_us/", views.contact_us, name="contact_us"),
    path("login/", views.login, name="login"),
    path("doctors/", views.doctors, name="doctors"),
    path("chatbot/", views.chatbot, name="chatbot"),

    # --------------------
    # USER DASHBOARD
    # --------------------
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),

    # --------------------
    # DOCTOR DASHBOARD
    # --------------------
    path("doctor_dashboard/", views.doctor_dashboard, name="doctor_dashboard"),

    # --------------------
    # ADMIN DASHBOARD
    # --------------------
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # --------------------
    # USER LOGIN / REGISTER API
    # FIXED: must match JS exactly → login-register (with hyphen)
    # --------------------
    path("api/user/login-register/", views.user_login_register_api, name="user_login_register_api"),

    # --------------------
    # ADMIN API
    # --------------------
    path("api/admin/login/", views.admin_login_api, name="admin_login_api"),
    path("api/admin/add-doctor/", views.admin_add_doctor_api, name="admin_add_doctor_api"),

    # --------------------
    # DOCTOR API
    # --------------------
    path("api/doctor/login/", views.doctor_login_api, name="doctor_login_api"),
    path("api/doctor/<str:doctor_name>/appointments/", views.doctor_appointments_api, name="doctor_appointments_api"),

    # --------------------
    # APPOINTMENT API
    # --------------------
    path("api/appointment/book/", views.book_appointment_api, name="book_appointment_api"),
    path("api/appointment/update/", views.update_appointment_api, name="update_appointment_api"),

    # --------------------
    # GENERAL API
    # --------------------
    path("api/doctors/all/", views.get_all_doctors, name="get_all_doctors"),
]
