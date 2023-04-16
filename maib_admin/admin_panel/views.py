from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .form import LoginForm, GeoForm
from django.contrib.auth import authenticate, login
from .models import Geo, Poster, Quiz, Question, Choice
# Create your views here.


def index(request):

    if request.user.is_authenticated:
        return render(request, 'index.html', {'name': request.user.username})
    else:
        return redirect('login/')
    
    


def poster(request):
    if request.user.is_staff:
        poster_list = Poster.objects.all()
        poster_len = len(poster_list)
    else:
        poster_list = Poster.objects.filter(author = request.user).all()
        poster_len = len(poster_list)
    return render(request, 'poster.html', {"poster_list": poster_list, "poster_len": poster_len})

def createposter(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        ageLim = request.POST.get('ageLim')
        desc = request.POST.get('desc')
        addinfo = request.POST.get('addinfo')
        addres = request.POST.get('addres')
        date = request.POST.get('date')
        author = request.user

        new_poster = Poster.objects.create(name = name, ageLim = ageLim, desc = desc, addinfo = addinfo, addres = addres, date = date, author = author)
        return redirect('/poster')


def editposter(request, id):
    poster_item = Poster.objects.get(id = id)

    if request.method == 'POST':
        poster_item.name = request.POST.get('name')
        poster_item.ageLim = request.POST.get('ageLim')
        poster_item.desc = request.POST.get('desc')
        poster_item.addinfo = request.POST.get('addinfo')
        poster_item.addres = request.POST.get('addres')
        poster_item.date = request.POST.get('date')

        poster_item.save()

    return redirect('/poster', id = poster_item.id)


def deleteposter(request, id):
    poster_item = Poster.objects.get(id = id)
    poster_item.delete()

    return redirect('/poster')

def geo(request):
    geo_list = Geo.objects.all()
    geo_len = len(geo_list)
    
    return render(request, 'geo.html', {'geo_list': geo_list, 'geo_len': geo_len})


def creategeo(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        link = request.POST.get('link')

        new_geo = Geo.objects.create(name=name, desc=desc, link=link)

    return redirect('/geo')

def deletegeo(request, id):
    geo_item = Geo.objects.get(id = id)
    geo_item.delete()


    return redirect('/geo')

def editgeo(request, id):
    geo_item = Geo.objects.get(id = id)

    if request.method == 'POST':
        geo_item.name = request.POST.get('name')
        geo_item.desc = request.POST.get('desc')
        geo_item.link = request.POST.get('link')

        geo_item.save()

    return redirect('/geo')
    

def quest(request):
    quest_list = Quiz.objects.all()
    quest_len = len(quest_list)

    
    return render(request, 'quests.html', {"quest_list": quest_list, "q_len": quest_len})

def add_quiz(request):
   if request.method == 'POST':
       title = request.POST['title']
       quiz = Quiz(title=title)
       quiz.save()

       for i in range(1, 11):
        textQ = request.POST.get(f'textQ_{i}')
        question = Question.objects.create(textQ=textQ, quiz=quiz)
        for j in range(1, 5):
            textC = request.POST.get(f'textC_{i}_{j}')
            iscorrect = request.POST.get(f'iscorrect_{i}_{j}')
            choice = Choice.objects.create(textC=textC, iscorrect=iscorrect, question=question)
   return redirect('/quest')

def delete_quiz(request, id):
    q_item = Quiz.objects.get(id = id)
    q_item.delete()


    return redirect('/quest')



def loginuser(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password'])
            
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/', {'name': request.user.username})
                # return render(request, 'index.html', {'name': request.user.username})
            else:
                return HttpResponse('Disabled account')

        else:
            return redirect('/invalid')


    return render(request, 'login.html', {'form': form})


def invalid_login(request):
    return render(request, 'invalid.html')
