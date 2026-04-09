from django.urls import path
from django.contrib.auth import views as auth_view
from . import views

urlpatterns=[
    path('', views.redirect_to_login, name='home'),
    path('register/',views.register,name='register'),
    path('login/',auth_view.LoginView.as_view(
        template_name='login.html'
    ),name='login'),
     path('logout/',
         auth_view.LogoutView.as_view(next_page='login'),
         name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('delete/<int:resume_id>/',views.delete_resume,name="delete_resume"),
    path('interview/<int:resume_id>/', views.start_interview, name='start_interview'),
    path("ai-suggest/", views.ai_suggest, name="ai_suggest"),
]