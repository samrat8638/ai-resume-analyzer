from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from . models import Resume
from . forms import ResumeUploadForm
import PyPDF2
import re
import ast

# Create your views here.
def register(request):
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=UserCreationForm()
    return render(request,'register.html',{'form':form})
    
@login_required
def dashboard(request):

    resumes = Resume.objects.filter(user=request.user)

    for resume in resumes:

        # Convert matched_skills safely
        if resume.matched_skills:
            try:
                resume.matched_skills = ast.literal_eval(resume.matched_skills)
            except:
                resume.matched_skills = {}
        else:
            resume.matched_skills = {}

        # Convert missing_skills safely
        if resume.missing_skills:
            try:
                resume.missing_skills = ast.literal_eval(resume.missing_skills)
            except:
                resume.missing_skills = {}
        else:
            resume.missing_skills = {}

    return render(request, "dashboard.html", {"resumes": resumes})

def redirect_to_login(request):
    return redirect('login')

@login_required
def upload_resume(request):

    if request.method == "POST":

        file = request.FILES["file"]
        selected_sector = request.POST.get("sector")

        resume = Resume.objects.create(
            user=request.user,
            file=file,
            sector=selected_sector
        )

        # -------- PDF TEXT EXTRACTION --------
        pdf_reader = PyPDF2.PdfReader(resume.file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        resume.extracted_text = text
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

        # -------- SKILL LIST --------
        SKILLS = {
            "tech": ["python", "django", "sql", "html", "css", "javascript", "react"],
            "commerce": ["accounting", "finance", "gst", "tax", "tally", "auditing"],
            "marketing": ["seo", "digital marketing", "content writing", "branding"],
            "engineering": ["autocad", "solidworks", "mechanical design"],
            "healthcare": ["patient care", "clinical research", "medical coding"],
        }

        sector_skills = SKILLS[selected_sector]

        matched = []
        missing = []

        for skill in sector_skills:
            if skill in text:
                matched.append(skill)
            else:
                missing.append(skill)

        score = (len(matched) / len(sector_skills)) * 100

        resume.matched_skills = str({selected_sector: matched})
        resume.missing_skills = str({selected_sector: missing})
        resume.score = score

        resume.save()

        return redirect("dashboard")

    return render(request, "upload.html")

import os
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Resume

@login_required
def delete_resume(request, resume_id):

    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == "POST":

        file_path = resume.file.path

        # delete database entry first
        resume.delete()

        # delete file safely
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except PermissionError:
            # file is currently open somewhere
            pass

    return redirect("dashboard")

   


# @login_required
# def start_interview(request, resume_id):

#     resume = Resume.objects.get(id=resume_id)

#     # convert string → dictionary
#     matched_skills = ast.literal_eval(resume.matched_skills)

#     # flatten skill list
#     skill_list = [skill.lower() for skills in matched_skills.values() for skill in skills]

#     print("Skill list:", skill_list)

#     # case-insensitive filtering
#     questions = Question.objects.filter(skill__in=[s.lower() for s in skill_list])
#     print("Questions found:", questions)

#     questions = random.sample(list(questions), min(5, len(questions)))

#     if request.method == "POST":

#         feedback = []

#         for question in questions:

#             answer = request.POST.get(f"answer{question.id}")

#             if not answer:
#                 feedback.append("No answer provided.")
#             elif len(answer) < 30:
#                 feedback.append("Answer too short. Add more explanation.")
#             else:
#                 feedback.append("Good answer length.")

#         return render(request, "interview_result.html", {
#             "feedback": feedback
#         })

#     return render(request, "interview.html", {
#         "questions": questions,
#         "resume": resume
#     })
    
import random
import ast
import os

from google import genai
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Resume, Question


# GEMINI CLIENT
client = genai.Client(api_key=settings.GEMINI_API_KEY)


@login_required
def start_interview(request, resume_id):

    resume = get_object_or_404(Resume, id=resume_id)

    matched_skills = ast.literal_eval(resume.matched_skills)

    skill_list = []

    for skills in matched_skills.values():
        skill_list.extend(skills)

    # ---------- GENERATE AI QUESTIONS ----------
    prompt = f"""
Generate 5 technical interview questions based on these skills:

{skill_list}

Return only the questions as a numbered list.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    questions = [q.strip() for q in response.text.split("\n") if q.strip()]

    # ---------- FEEDBACK ----------
    if request.method == "POST":

        answers = []

        for i, q in enumerate(questions):

            answer = request.POST.get(f"answer{i+1}")

            answers.append(f"Question: {q}\nAnswer: {answer}")

        feedback_prompt = f"""
Evaluate the following interview answers and give short feedback.

{answers}
"""

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=feedback_prompt
        )

        feedback = result.text.split("\n")

        return render(request, "interview_result.html", {
            "feedback": feedback
        })

    return render(request, "interview.html", {
        "questions": questions
    })
    
    
from google import genai
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

client = genai.Client(api_key=settings.GEMINI_API_KEY)


@login_required
def ai_suggest(request):

    response_text = None

    if request.method == "POST":

        user_prompt = request.POST.get("prompt")

        system_prompt = f"""
You are an AI career assistant.

Help users with:

- Missing skills suggestions
- Resume improvement tips
- Job description writing
- Career guidance

User request:
{user_prompt}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt
        )

        response_text = response.text

    return render(request, "ai_suggest.html", {
        "response": response_text
    })