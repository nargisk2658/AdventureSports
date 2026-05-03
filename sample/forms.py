from django import forms 
from django.core.exceptions import ValidationError
from .models import User,UserLogin,DemoDate
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, str(email)):
        raise ValidationError('Please enter a valid email address')

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long')
    return password

class userdataForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={'required': 'Email is required', 'invalid': 'Please enter a valid email'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        validators=[validate_password],
        error_messages={'required': 'Password is required'}
    )
    
    class Meta:
        model=User
        fields="__all__"
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
        }

class UserLoginForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email',
            'id': 'email'
        }),
        error_messages={'required': 'Email is required', 'invalid': 'Please enter a valid email'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password',
            'id': 'password'
        }),
        error_messages={'required': 'Password is required'}
    )
    
    class Meta:
        model=UserLogin
        fields="__all__"
        widgets={'password':forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})}

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            validate_email(email)
            validate_password(password)
        
        return cleaned_data

class DemoDateForm(forms.ModelForm):
	class Meta:
		model=DemoDate
		fields="__all__"
		widgets = {'demodate': forms.DateInput(),}

