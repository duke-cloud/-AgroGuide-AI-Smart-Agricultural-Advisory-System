from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import FarmerProfile

NIGERIA_STATES = [
    ('', '-- Select State --'),
    ('Abia','Abia'), ('Adamawa','Adamawa'), ('Akwa Ibom','Akwa Ibom'),
    ('Anambra','Anambra'), ('Bauchi','Bauchi'), ('Bayelsa','Bayelsa'),
    ('Benue','Benue'), ('Borno','Borno'), ('Cross River','Cross River'),
    ('Delta','Delta'), ('Ebonyi','Ebonyi'), ('Edo','Edo'), ('Ekiti','Ekiti'),
    ('Enugu','Enugu'), ('FCT','FCT - Abuja'), ('Gombe','Gombe'),
    ('Imo','Imo'), ('Jigawa','Jigawa'), ('Kaduna','Kaduna'), ('Kano','Kano'),
    ('Katsina','Katsina'), ('Kebbi','Kebbi'), ('Kogi','Kogi'),
    ('Kwara','Kwara'), ('Lagos','Lagos'), ('Nasarawa','Nasarawa'),
    ('Niger','Niger'), ('Ogun','Ogun'), ('Ondo','Ondo'), ('Osun','Osun'),
    ('Oyo','Oyo'), ('Plateau','Plateau'), ('Rivers','Rivers'),
    ('Sokoto','Sokoto'), ('Taraba','Taraba'), ('Yobe','Yobe'), ('Zamfara','Zamfara'),
]

class FarmerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name  = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email      = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone      = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+234...'}))
    state      = forms.ChoiceField(choices=NIGERIA_STATES)
    lga        = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.state = self.cleaned_data.get('state', '')
            user.profile.lga   = self.cleaned_data.get('lga', '')
            user.profile.save()
        return user


class FarmerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name  = forms.CharField(max_length=50)
    email      = forms.EmailField()
    state      = forms.ChoiceField(choices=NIGERIA_STATES)

    class Meta:
        model  = FarmerProfile
        fields = ['phone', 'state', 'lga', 'village', 'latitude', 'longitude',
                  'preferred_language', 'profile_picture', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial  = self.instance.user.last_name
            self.fields['email'].initial      = self.instance.user.email
