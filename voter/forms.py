from django import forms
from django.core.exceptions import ValidationError
from .models import Voter
import datetime


class VoterLoginForm(forms.Form):
    # Changed from Aadhaar to wallet address/email
    username = forms.CharField(label="Email or Ethereum Address") 
    password = forms.CharField(label="Temporary Password", widget=forms.PasswordInput)


    
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email")
