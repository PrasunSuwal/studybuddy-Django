from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import Room, Topic, Message, Profile
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
import re
from django.core.files.storage import FileSystemStorage


# Create your views here.

def index(request):
    rooms = Room.objects.all()
    #topic = Topic.objects.all()[:5]
    topic = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:5]
    message_room = Message.objects.all()
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    users = User.objects.all()
    
    return render(request, "base/index.html",{'rooms': rooms, 'topics': topic, 'room_count': rooms.count(), 'message_room': message_room })

def room(request,slug):
    #room = get_object_or_404(Room, slug = slug)
    room = Room.objects.get(slug=slug)
    messages = room.message_set.all()
    participants = room.participants.all()
    host = participants.get(id=room.host.id)
            
    if request.method == "POST":
        Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', slug=room.slug)
    return render(request, "base/room.html", {'room': room, 'chats': messages, 'participants': participants, 'host':host })


def serialize_topic(topic):
    return {
        'name': topic.name,
        'room_count': topic.room_set.count(),
    }
    
def topics(request):
    room_count = Room.objects.all().count()
    topic = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')
    paginator = Paginator(topic, 5)
    page_number = request.GET.get("page",1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'items':  [serialize_topic(t) for t in page_obj.object_list],  
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
        return JsonResponse(data, safe=False)
    else:
        return render(request, "base/alltopics.html", {'page_obj': page_obj, 'room_count':room_count, 'current_page': page_number})



def activity(request):
    return render(request, "base/activity.html")


def profile(request,username):
    profile_user = User.objects.get(username=username)
    rooms = Room.objects.filter(host=profile_user)
    topic = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:5]
    message_room = Message.objects.all()
    profile = Profile.objects.get(user=profile_user)
   
    return render(request, "base/profile.html",{'topics':topic, 'message_room': message_room, 'rooms':rooms, 'room_count': rooms.count(), 'profile_user': profile_user, 'profile': profile })



def userLogin(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,"User does not exist")
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Username or password does not match")

    if request.user.is_authenticated:
        return redirect('index')
    
    context = {'page': page}
    return render(request, "base/login.html", context) 


def userLogout(request):
    logout(request)
    return redirect('login')
    

def signUp(request):
    # if request.user.is_authenticated:
    #     return render('index')
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
    
        if(fullname == '' and username == '' and password == '' and confirm_password == ''):
            return redirect(reverse('signup'))
        elif(password != confirm_password):
            return redirect(reverse('signup'))
        else:         
             user = User.objects.create_user(username=username, password=password)
             user.first_name = fullname.split()[0]
            #  asd = fullname.split(' ');
            #  print(asd)
             user.last_name = ' '.join(fullname.split()[1:])
             user.save()
             login(request, user)
             return redirect('index')
        
    return render(request, "base/signup.html")


def createRoom(request):
    topics = Topic.objects.all()
    context = {'topics': topics}
    
    if request.method == 'POST':
        name = request.POST.get('room_name')
        topic = request.POST.get('topic')
        Unrefine_slug = name +"-"+ topic
        value = re.sub(r'[^a-zA-Z0-9]+', '-', Unrefine_slug)
        slug = value.strip('-').lower()
        description = request.POST.get('room_about')
        host = request.user
        id = isNum(topic)
        
        if(id):
            topic_instance = Topic.objects.get(id = topic)
            topic = topic_instance
        else:
            topic_instance = Topic.objects.create(name = topic)
            topic = topic_instance
            
        update = request.POST.get('update')
                  
        if(update is not None):
            Room.objects.filter(slug=update).update(
                name = name,
                topic = topic,
                description = description,
                slug = slug,
                host = host  
            )
            messages.success(request,"Updated Successfully", extra_tags="updated_success")
        else:
            room =  Room.objects.create(
                name = name,
                topic = topic,
                description = description,
                slug = slug,
                host = host     
            )
            room.participants.add(request.user)
            messages.success(request,"Created Successfully", extra_tags="created_success")
        return redirect('index')
    return render(request, "base/create-room.html", context)

def editRoom(request,slug):
    data = Room.objects.get(slug = slug)
    return render(request, "base/create-room.html", {'data' : data})

def deleteRoom(request, slug):
    if request.method == "POST":
        room = Room.objects.get(slug=slug)
        if request.user == room.host:
            room.delete()
            return redirect('index')
        else:
            return render(request, "base/create-room.html")
    
def deleteMessage(request,slug):
    if request.method == "POST":
        pk = request.POST.get('id')
        message= Message.objects.get(id=pk)
        if request.user == message.user:
            message.delete()
            return redirect('room', slug=slug)    
    return redirect('room')
    
def isNum(topic):
    try:
        int(topic)
        id = True
        return id
    except ValueError:
        id = False 
        return id

def editUser(request):
    user = request.user
    profile = user.profile_set.get()
    if request.method == "POST":
        if 'image' in request.FILES:
            image = request.FILES.get('image')
            getfullname = request.POST.get('fullname')
            fullname = getfullname.split(' ')
                       
            user.first_name =  fullname[0]
            user.last_name =  fullname[1]
            user.save()
            
            Profile.objects.update_or_create(
                user = user,
                defaults={"image":image},
                create_defaults={"image":image}
            )  
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            about = request.POST.get('about')
            
            user.username = username
            user.email = email
            user.save()
            
            Profile.objects.update_or_create(
                user = user,
                defaults={"about":about},
                create_defaults={"about":about}
            )
        messages.success(request, "Updated Successfully", extra_tags="updated_success")
        return redirect('profile', username= user.username)
    return render(request, "base/edit-user.html",{'profile':profile})

def settings(request):
    #user = request.user
    #profile = user.profile.get()
    return render(request, "base/settings.html")
    
def delete(request):
    return render(request, "base/delete.html")




