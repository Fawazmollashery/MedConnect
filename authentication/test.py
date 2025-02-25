import google.generativeai as genai

genai.configure(api_key="AIzaSyDy7rzWXYrbzCM001k0Aic22O93k7xZEmM")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("who is the father of nation india")
print(response.text)