from django.contrib import admin
from . models import Question,Resume

# Register your models here.




@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "sector",
        "score",
        "upload_at"
    )

    search_fields = (
        "user__username",
        "sector"
    )

    list_filter = (
        "sector",
        "upload_at"
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = ("id","skill","question_text")