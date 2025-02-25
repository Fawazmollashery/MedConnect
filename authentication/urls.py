from django.contrib import admin
from django.urls import path
from . import views  # Import views from your app
from authentication.views import chatbot_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Home page
    path('signin/', views.signin, name='signin'),  # Sign In page
    path('signup/', views.signup, name='signup'),  # Sign Up page
    path('instruction/', views.instruction, name='instruction'),
    path('chatbot/', views.chatbot_view, name='chatbot_view'),  # Chatbot page
    path('chatbot/download_prescription/<int:chat_id>/', views.download_prescription, name='download_prescription'),  # Download prescription
    #path('send_prescription/<int:chat_id>/', views.send_prescription, name='send_prescription'),
    # path('download_and_send_prescription/<int:chat_id>/', views.download_and_send_prescription, name='download_and_send_prescription'),
    path('chatbot/email_prescription/<int:chat_id>/', views.email_prescription, name='email_prescription'),  # Email prescription   
]