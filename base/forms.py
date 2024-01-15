from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username', 'email', 'password1','password2']

class RoomForm(ModelForm): 
    
    class Meta:
        model = Room
        fields = '__all__' #this copies all the variables in the models.py, ie: 'host', topic, etc and presents it as data
        exclude = ['host', 'participants'] 
        
class UserForm(ModelForm):
    class Meta:
        model = User
        fields=['avatar', 'name','username', 'email','bio']