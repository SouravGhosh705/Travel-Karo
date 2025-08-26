from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with Indian-specific fields"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91XXXXXXXXXX'
        }),
        help_text='Mobile number with country code (+91 for India)'
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Optional: Your date of birth'
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + User.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 
                 'date_of_birth', 'gender', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces or dashes
            phone = phone.replace(' ', '').replace('-', '')
            
            # Check if it starts with +91 or is 10 digits
            if phone.startswith('+91') and len(phone) == 13:
                return phone
            elif phone.startswith('91') and len(phone) == 12:
                return '+' + phone
            elif len(phone) == 10 and phone.isdigit():
                return '+91' + phone
            else:
                raise forms.ValidationError(
                    'Please enter a valid Indian mobile number (10 digits or +91XXXXXXXXXX)'
                )
        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            # Check if user is at least 13 years old
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 13:
                raise forms.ValidationError('You must be at least 13 years old to register.')
        return dob


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username or email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 
            'gender', 'address', 'city', 'state', 'pin_code', 'aadhaar_number'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '6'}),
            'aadhaar_number': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '12',
                'placeholder': 'XXXXXXXXXXXX (12 digits)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty choice for state dropdown
        self.fields['state'].choices = [('', 'Select State')] + list(User.STATE_CHOICES)
        self.fields['gender'].choices = [('', 'Select Gender')] + list(User.GENDER_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces or dashes
            phone = phone.replace(' ', '').replace('-', '')
            
            # Check if it starts with +91 or is 10 digits
            if phone.startswith('+91') and len(phone) == 13:
                return phone
            elif phone.startswith('91') and len(phone) == 12:
                return '+' + phone
            elif len(phone) == 10 and phone.isdigit():
                return '+91' + phone
            else:
                raise forms.ValidationError(
                    'Please enter a valid Indian mobile number'
                )
        return phone

    def clean_pin_code(self):
        pin_code = self.cleaned_data.get('pin_code')
        if pin_code and (not pin_code.isdigit() or len(pin_code) != 6):
            raise forms.ValidationError('PIN code must be exactly 6 digits')
        return pin_code

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number')
        if aadhaar:
            # Remove any spaces or dashes
            aadhaar = aadhaar.replace(' ', '').replace('-', '')
            if not aadhaar.isdigit() or len(aadhaar) != 12:
                raise forms.ValidationError('Aadhaar number must be exactly 12 digits')
        return aadhaar
