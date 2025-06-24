from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.voter_signin, name='voter_signin'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('candidates/', views.candidates_info_list, name='candidates_info_list'),
    path('voting/', views.voting_page, name='voting_page'),
    path('submit-vote/', views.submit_vote, name='submit_vote'),
    path('logout/', views.voter_logout, name='voter_logout'),
    path('results/', views.voting_results, name='voting_results'),
    path('dashboard/', views.voter_dashboard, name='voter_dashboard'),
]
