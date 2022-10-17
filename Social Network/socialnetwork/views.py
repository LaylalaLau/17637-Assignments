
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone, dateformat, formats

from django.http import HttpResponse, Http404

from socialnetwork.forms import LoginForm, RegisterForm, GlobalStreamForm, ProfileForm
from socialnetwork.models import Profile, Post, Comment

import json

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))

@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    new_profile = Profile(user=new_user)
    new_profile.save()

    login(request, new_user)
    return redirect(reverse('home'))

@login_required
def global_stream_action(request):
    context = {}
    context['page_name'] = "Global Stream"

    if not request.user.is_anonymous:
        context['current_user'] = request.user.first_name + " " + request.user.last_name

    return render(request, 'stream.html', context)
    return redirect(reverse('login'))

@login_required
def follower_stream_action(request):
    context = {}
    context['page_name'] = "Follower Stream"

    if not request.user.is_anonymous:
        context['current_user'] = request.user.first_name + " " + request.user.last_name

    return render(request, 'stream.html', context)

@login_required
def profile_action(request):
    context = {}
    context['profile_name'] = request.user.first_name + " " + request.user.last_name
    context['current_user'] = context['profile_name']
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['profile'] = request.user.profile
        context['form'] = ProfileForm(initial={'bio': request.user.profile.bio})
        return render(request, 'profile.html', context)

    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context['form'] = form
        context['profile'] = request.user.profile
        return render(request, 'profile.html', context)

    profile = get_object_or_404(Profile, id=request.user.id)
    profile.picture = form.cleaned_data['picture']
    profile.content_type = form.cleaned_data['picture'].content_type
    profile.bio = form.cleaned_data['bio']
    profile.save()

    context['profile'] = request.user.profile
    context['form'] = ProfileForm(initial={'bio': request.user.profile.bio})
    return render(request, 'profile.html', context)

@login_required
def other_profile_action(request, id):
    context = {}
    current_user = request.user
    context['current_user'] = current_user.first_name + " " + current_user.last_name
    user = User.objects.get(id=id)
    context['profile'] = user.profile
    context['form'] = ProfileForm(initial={'bio': request.user.profile.bio})
    return render(request, 'other_profile.html', context)

@login_required
def get_photo(request, id):
    profile = get_object_or_404(Profile, id=id)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not profile.picture:
        raise Http404

    return HttpResponse(profile.picture, content_type=profile.content_type)

@login_required
def unfollow(request, id):
    user_to_unfollow = User.objects.get(id=id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()

    context = {}
    context['current_user'] = request.user.first_name + " " + request.user.last_name
    context['profile'] = user_to_unfollow.profile
    return render(request, 'other_profile.html', context)

@login_required
def follow(request, id):
    user_to_follow = User.objects.get(id=id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()

    context = {}
    context['current_user'] = request.user.first_name + " " + request.user.last_name
    context['profile'] = user_to_follow.profile
    return render(request, 'other_profile.html', context)


def get_list_json_dumps_serializer(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    response_data = {'posts': [],
                     'comments': []}
    all_comments = Comment.objects.all()
    for c in all_comments:
        comment = {
            'id': c.id,
            'text': c.text,
            'creation_time': c.creation_time.isoformat(" ", "auto"),
            'user_id': c.creator.id,
            'username': c.creator.first_name + " " + c.creator.last_name,
            'post_id': c.post.id
        }
        response_data['comments'].append(comment)
    for model_item in Post.objects.all():
        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            # 'creation_time': formats.date_format(model_item.creation_time, "n/j/Y g:i A"),
            'creation_time': model_item.creation_time.isoformat(" ", "auto"),
            'user_id': model_item.user.id,
            'username': model_item.user.first_name + " " + model_item.user.last_name,
            'comments': []
        }
        for c in all_comments:
            if c.post.user.id == model_item.user.id:
                my_item['comments'].append(c.id)
        response_data['posts'].append(my_item)

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)

def add_post(request):
    post = Post(text=request.POST['text'], user=request.user, creation_time=timezone.now())
    post.save()
    return get_list_json_dumps_serializer(request)

def add_comment(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not 'comment_text' in request.POST or not request.POST['comment_text'] or \
        not 'post_id' in request.POST or not request.POST['post_id']:
        return _my_json_error_response("You must enter an item to add.", status=400)

    try:
        post_id = int(request.POST['post_id'])
        comment_text = request.POST['comment_text']
        post = Post.objects.get(id=post_id)
    except:
        return _my_json_error_response("You're hacking!", status=400)

    new_item = Comment(text=comment_text,
                       creator=request.user,
                       creation_time=timezone.now(),
                       post=post)
    new_item.save()

    response = {
        'posts': [],
        'comments': [
            {'id': new_item.id,
            'text': new_item.text,
            'creation_time': new_item.creation_time.isoformat(" ", "auto"),
            'user_id': new_item.creator.id,
            'username': new_item.creator.first_name + " " + new_item.creator.last_name,
            'post_id': new_item.post.id}
        ]
    }
    response_json = json.dumps(response)

    return get_follower_stream(request)
    # return HttpResponse(response_json, content_type='application/json')

def get_follower_stream(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    response_data = {'posts': [],
                     'comments': []}
    all_comments = Comment.objects.all()
    all_posts = Post.objects.all()
    follower_posts = []
    for p in all_posts:
        if p.user in request.user.profile.following.all():
            follower_posts.append(p)
    for model_item in follower_posts:
        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            'creation_time': model_item.creation_time.isoformat(" ", "auto"),
            'user_id': model_item.user.id,
            'username': model_item.user.first_name + " " + model_item.user.last_name,
            'comments': []
        }
        for c in all_comments:
            if c.post.user.id == model_item.user.id:
                my_item['comments'].append(c.id)
                comment = {
                    'id': c.id,
                    'text': c.text,
                    'creation_time': c.creation_time.isoformat(" ", "auto"),
                    'user_id': c.creator.id,
                    'username': c.creator.first_name + " " + c.creator.last_name,
                    'post_id': c.post.id
                }
                response_data['comments'].append(comment)
        response_data['posts'].append(my_item)

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')
