from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.admin_register, name='admin_register'),
    path('login/', views.admin_login, name='admin_login'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/add/', views.add_candidate, name='add_candidate'),
    path('candidates/update/<int:pk>/', views.update_candidate, name='update_candidate'),
    path('candidates/delete/<int:pk>/', views.delete_candidate, name='delete_candidate'),
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    # Voter Management
    path('voters/', views.voter_list, name='voter_list'),
    path('voters/add/', views.add_voter, name='add_voter'),
    path('voters/update/<int:pk>/', views.update_voter, name='update_voter'),
    path('voters/delete/<int:pk>/', views.delete_voter, name='delete_voter'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('forgot-pass/', views.forgot_pass, name='forgot_pass'),
    # Utility Endpoints
    path('schedule/', views.schedule_list, name='schedule_list'),
    path('schedule/add/', views.add_schedule, name='add_schedule'),
    path('schedule/update/<int:pk>/', views.update_schedule, name='update_schedule'),
    path('schedule/delete/<int:pk>/', views.delete_schedule, name='delete_schedule'),
    path('overall-results/', views.overall_results, name='overall_results'),
    path('set-voting-period/', views.initialize_voting_period, name='initialize_voting_period'),
]
