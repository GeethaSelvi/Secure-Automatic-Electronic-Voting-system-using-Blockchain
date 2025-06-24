from django import forms
from django.core.exceptions import ValidationError
from .models import Candidate, AdminUser, Schedule
from voter.models import Voter
from captcha.fields import CaptchaField
from adminapp.models import hash_password

# Candidate Management Form
class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            'name', 'party_name', 'date_of_birth', 'state', 'district', 
            'region', 'election_place', 'pincode', 'image', 'symbol_image'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

# Voter Management Form
# vo/voting/adminapp/forms.py

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['name', 'date_of_birth', 'mobile_number', 'email', 
                 'address', 'pincode', 'region', 'state', 'district', 'current_place']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        if Voter.objects.exclude(pk=self.instance.pk).filter(mobile_number=mobile_number).exists():
            raise ValidationError("This mobile number is already registered.")
        return mobile_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if Voter.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email



class AdminRegisterForm(forms.ModelForm):
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()

    class Meta:
        model = AdminUser
        fields = ['username', 'fullname', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')

        if password and repeat_password and password != repeat_password:
            raise ValidationError("Passwords do not match.")
        
        # Hash password before storage
        if password:
            cleaned_data['password'] = hash_password(password)
        return cleaned_data




class AdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['election_name', 'election_date', 'region', 'state', 'description']
        widgets = {
            'election_date': forms.DateInput(attrs={'type': 'date'}),
        }
