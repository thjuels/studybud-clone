from django.shortcuts import render, redirect

# Create your views here.
#called when someone goes to a certain url

#After the rooms database has been created in models...
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# rooms = [
#     {'id':1, 'name':'Lets learn react'},
#     {'id':2, 'name':'Design with me'},
#     {'id':2, 'name':'Linkedin tips'},
# ]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")
            
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username OR Password does not exist!")
        
    context = {'page':page}
    return render(request, 'base/login-register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    #page = 'register'
    form = MyUserCreationForm
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower() # makes it lowercase, 'cleaning' name
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occured during registration.')
    
    context = {#'page':page,
               'form':form,
               }
    return render(request, 'base/login-register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    #room_messages = Message.objects.all() #can change to modify to only see people you follow 
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) #ie
    
    
    
    context = {'rooms': rooms, 
               'topics': topics, 
               'room_count': room_count,
               'room_messages': room_messages,
               }
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    roomMessages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    
    if request.method =="POST":
        messages = Message.objects.create(
            user=request.user,
            body=request.POST.get('body'),
            room=room,
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 
               'roomMessages': roomMessages,
               'participants': participants,
               }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    
    context = {'user':user,
               'rooms':rooms,
               'room_messages': room_messages,
               'topics':topics,
               }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    
    topics = Topic.objects.all()
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form = RoomForm(request.POST) # previous form function
        # if form.is_valid():
        #     room = form.save()
        #     room.host = request.user
        #     form.save()
        return redirect('home')
    
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room-form.html', context) #variable passed in, so can be used in room-form.html

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #prefilled with the current data values of the room
    
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    
    if request.method == "POST":
        # form = RoomForm(request.POST, instance=room) #instance=room to make sure current room is being edited
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request,'base/room-form.html',context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    
    if request.method == "POST":
        room.delete() 
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("You are not allowed here")
    
    if request.method == "POST":
        message.delete() 
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': message})

@login_required
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    
    context = {'form':form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()

    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html', context)