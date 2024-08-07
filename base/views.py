from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm




def loginPage(request):
    
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method == "POST":
        
        # get username and password from the submit form
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        # check if the user exits or not. if not then flash message.
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exists.')
            
        # authenticate the username and password. correct or not. if not it return None.    
        user = authenticate(request, email=email, password=password)
        
        # if auth works then login and redirect to home
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'email or password incorrect.')
            
    context= {'page' : page}
    return render(request, 'base/login_register.html', context)




def logoutPage(request):
    logout(request)
    return redirect('home')




def registerPage(request):
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
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
    
    topics = Topic.objects.all()[:5]
    
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
    topics = Topic.objects.all()
    
    # if its a form submit then request method will be "POST"
    # to check the 'POST' data
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        
        #get_or_create will get the topic name. if a topic name exits,
        #then created will be False, else if topic name is newly created,
        #then created will be True
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        
        """  # the auto method to assign the form data. 
        # request.POST is a dict of values submitted to form.
        # this will create new entry in the database.
        form = RoomForm(request.POST)
        
        # to verify the data is assigned correctly
        if form.is_valid():
            
            # if verified then save the data. 
            # before this data is not stored in the database. 
            room = form.save(commit=False)
            room.host = request.user
            room.save() """
            
        # redirecting after saving data
        return redirect('home')
        
    
    context = {'form' : form, 'topics':topics}
    return render(request, 'base/room_form.html', context)




# this decorator restrict the user if not login to go to specified url
@login_required(login_url='login')
def updateRoom(request, pk):
    topics = Topic.objects.all()
    
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
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        

        room.topic=topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context = {"form" : form, 'topics':topics, 'room':room}
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



@login_required(login_url='login')
def editUser(request,pk):
    user = User.objects.get(id=pk)
    form = UserForm(instance=request.user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id )
    
    context ={'user':user, 'form':form}
    return render(request, 'base/edit-user.html', context)



def topicPage(request):
    q = request.GET.get('q')
    
    if q == None:
        q=''
        
    topics = Topic.objects.filter(Q(name__icontains=q))
    room_count = Room.objects.filter(Q(topic__name__icontains=q)).count()
    return render(request, 'base/topics.html', {'topics':topics, 'room_count':room_count})



def activityPage(request):
    q = request.GET.get('q')
    
    if q == None:
        q=''
        
    roomMessages = Message.objects.filter(Q(room__name__icontains=q))
    
    return render(request, 'base/activity.html', {'roomMessages':roomMessages})