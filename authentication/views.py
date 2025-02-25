from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from django.utils import timezone
from email.mime.application import MIMEApplication
from django.conf import settings

import json
import resend
import requests
from .models import Chat
from .utils import generate_prescription_pdf
import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key='AIzaSyDy7rzWXYrbzCM001k0Aic22O93k7xZEmM')
model = genai.GenerativeModel('gemini-pro')


# Home Page View
def home(request):
    return render(request, 'index.html')

def instruction(request):
    return render(request, 'instruction.html')


# Signup Page View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('signin')

    return render(request, 'signup.html')



# Signin Page View
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Username: {username}, Password: {password}")  # Debugging

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Login successful!")  # Debugging
            return redirect("/")  # Redirect to home page
        else:
            print("Invalid credentials!")  # Debugging
            messages.error(request, 'Invalid username or password')

    return render(request, 'signin.html')


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
import json
from .models import Chat  # Ensure Chat model is imported
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
import json
from .models import Chat




@login_required(login_url='signin')
def chatbot_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)

            # Handle prescription download
            if user_message.lower() == "download prescription":
                last_chat = Chat.objects.filter(user=request.user).order_by('-created_at').first()
                if last_chat:
                    return JsonResponse({
                        'response': 'Your prescription is ready for download.',
                        'status': 'success',
                        'chat_id': last_chat.id,
                        'show_download_button': True
                    })
                return JsonResponse({
                    'response': 'No recent prescriptions found. Please ask a question first.',
                    'status': 'error',
                    'show_download_button': False
                })

            # Updated prompt for line-by-line response
            prompt = f"""
            You are a virtual doctor providing concise medical advice. 
            Do NOT use any special characters like *, **, or markdown formatting. 
            Write responses in PLAIN TEXT with LINE BREAKS between sections.

            Important Instructions:
            - DO NOT write paragraphs. Use short, simple sentences.
            - Separate each section (Assessment, Remedies, Medications) with line breaks.
            - List remedies and medications using numbers (1, 2, 3).
            - Avoid greetings like "Hello, I'm Dr. MedBot."

            Example Response Format:
            Assessment:
            [One short sentence about the condition.]

            Remedies:
            1. [First remedy]
            2. [Second remedy]
            3. [Third remedy]

            Medications (if necessary):
            1. [Medicine name, dosage, timing, special instructions]
            2. [Second medicine, if required]

            Patient's question: {user_message}
            """

            # Generate response
            response = model.generate_content(prompt)
            generated_text = response.text.strip()

            # Save chat history
            chat = Chat(
                user=request.user,
                message=user_message,
                response=generated_text,
                created_at=timezone.now()
            )
            chat.save()

            return JsonResponse({
                'response': generated_text,
                'status': 'success',
                'chat_id': chat.id,
                'show_download_button': False
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid message format', 'status': 'error'}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': 'An error occurred. Please try again later.'}, status=500)

    chats = Chat.objects.filter(user=request.user).order_by('created_at')
    username = request.user.username  # Fetch the signed-in user's name
    return render(request, 'chatbot.html', {
        'chats': list(chats.values('message', 'response', 'id')),
        'username': username  # Pass the username to the template
    })



# Download Prescription View
@login_required(login_url='signin')
def download_prescription(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        pdf = generate_prescription_pdf(
            user=request.user,
            message=chat.message,
            response=chat.response
        )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="prescription_{chat_id}.pdf"'
        response.write(pdf)
        return response
    except Chat.DoesNotExist:
        return HttpResponse("Prescription not found", status=404)
    except Exception as e:
        print(f"Error: {str(e)}")
        return HttpResponse("An error occurred while generating the prescription.", status=500)


# Email Prescription View

@login_required(login_url='signin')
def email_prescription(request, chat_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        
        # Generate PDF
        pdf = generate_prescription_pdf(
            user=request.user,
            message=chat.message,
            response=chat.response
        )
        
        # Email setup
        sender_email = "mollasheryfawaz@gmail.com"
        receiver_email = request.user.email
        subject = f"Your Medical Prescription - {timezone.now().strftime('%Y-%m-%d')}"
        body = f"""
        Dear {request.user.first_name or request.user.username},
        
        Please find your medical prescription attached.
        
        Best regards,
        MedBot Team
        """
        
        # Create email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        
        # Attach body text
        message.attach(MIMEText(body, "plain"))
        
        # Attach PDF properly
        pdf_attachment = MIMEApplication(pdf, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"prescription_{chat_id}.pdf")
        message.attach(pdf_attachment)
        
        # SMTP connection and send
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_password = "olhk hcnf oyow ibry"
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(message)
        
        return JsonResponse({'status': 'success', 'message': 'Prescription sent to your email'})
        
    except Chat.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Prescription not found'}, status=404)
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)






