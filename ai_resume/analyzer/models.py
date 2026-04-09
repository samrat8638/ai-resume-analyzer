from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):

    SECTOR_CHOICES = [
        ("tech", "Tech"),
        ("commerce", "Commerce"),
        ("marketing", "Marketing"),
        ("engineering", "Engineering"),
        ("healthcare", "Healthcare"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)

    # ✅ NEW FIELD (Only addition)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)

    matched_skills = models.TextField(blank=True, null=True)
    missing_skills = models.TextField(blank=True, null=True)
    score = models.FloatField(null=True, blank=True)

    upload_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Question(models.Model):
    skill=models.CharField(max_length=255)
    question_text=models.TextField()
    def __str__(self):
        return self.skill