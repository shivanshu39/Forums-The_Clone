from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from .forms import RoomForm




def loginPage(request):
    
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method == "POST":
        
        # get username and password from the submit form
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        # check if the user exits or not. if not then flash message.
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists.')
            
        # authenticate the username and password. correct or not. if not it return None.    
        user = authenticate(request, username=username, password=password)
        
        # if auth works then login and redirect to home
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'username or password incorrect.')
            
    context= {'page' : page}
    return render(request, 'base/login_register.html', context)




def logoutPage(request):
    logout(request)
    return redirect('home')




def registerPage(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'An error during registration.')
    
    context = {'form': form}
    
    return render(request, 'base/login_register.html', context)



def home(request):
    q = request.GET.get('q')
    
    if q == None:
        q=''
    
    # chaining the search parameters with &(and), |(or) using Q function of django
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q)
                                )
    
    topics = Topic.objects.all()
    
    room_count = rooms.count()
    
    roomMessages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
    
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'roomMessages': roomMessages}
    return render(request, 'base/home.html', context)




def room(request, pk):
    
    room = Room.objects.get(id=pk)
    
    roomMessages = room.message_set.all().order_by('created') # type:ignore
    
    participants = room.participants.all()        
            
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('body')            
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id) # type:ignore
            
    context= {'room':room, 'roomMessages':roomMessages, 'participants':participants}
    
    return render(request, 'base/room.html', context)




def chat(request):
    return render(request, 'base/chat.html')




@login_required(login_url='login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # type:ignore
    topics = Topic.objects.all()
    roomMessages = user.message_set.all() # type:ignore
    room_counter = Room.objects.all()
    count =0
    for i in room_counter:
        count+=1
    room_count=count
    
    context = {'user':user, 'rooms':rooms, 'topics':topics, 'roomMessages':roomMessages, 'room_count':room_count}
    return render(request, 'base/profile.html', context)



# this decorator restrict the user if not login to go to specified url
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    
    # if its a form submit then request method will be "POST"
    # to check the 'POST' data
    if request.method == 'POST':
        
        # the auto method to assign the form data. 
        # request.POST is a dict of values submitted to form.
        # this will create new entry in the database.
        form = RoomForm(request.POST)
        
        # to verify the data is assigned correctly
        if form.is_valid():
            
            # if verified then save the data. 
            # before this data is not stored in the database. 
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            
            # redirecting after saving data
            return redirect('home')
    
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)




# this decorator restrict the user if not login to go to specified url
@login_required(login_url='login')
def updateRoom(request, pk):
    
    # pk - primary key
    # using pk we get which room is going to be updated.
    room = Room.objects.get(id=pk)
    
    # form will be pre-filled with the values of the room passed to it.
    # instance is like "show the values from this database."
    form = RoomForm(instance=room)
   
   
    # to restrict other user except the room host to update
    if request.user != room.host:
        return HttpResponse('you do not have access.')
   
   
   #now updating the data into the database  
    if request.method == 'POST':
        
        # instance will tell which database entry to update rather than creating a new entry in the database.
        form = RoomForm(request.POST, instance=room)
        
        if form.is_valid():
            
            form.save()
            return redirect('home')
    
    context = {"form" : form}
    return render(request, 'base/room_form.html', context)




# this decorator restrict the user if not login to go to specified url
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    
    # to restrict other user except the room host to update
    if request.user != room.host:
        return HttpResponse('you do not have access.')
    
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    
    context = {'obj' : room}
    return render(request, 'base/delete.html', context)



@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('you do not have access.')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home') 
    context={'obj': message}
    return render(request,'base/delete.html',context)