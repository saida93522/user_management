from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post
from .forms import RegisterForm, PostForm
import logging

logging.basicConfig(level=logging.DEBUG,filename='view.log',filemode="w",
                    format='%(asctime)s - %(levelname)s - %(message)s')



@login_required(login_url='/login')
def home(request):
    posts = Post.objects.select_related().all()
    if request.method == 'POST':
        post_id = request.POST.get('post-id')
        user_id = request.POST.get('user-id')

        if post_id:
            post = Post.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm('auth_app.delete_post')):
                post.delete()
                
        elif user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                try:
                    # ban user by removing them from default group
                    group = Group.objects.get(name='default')
                    group.user_set.remove(user)
                except PermissionDenied as exc:
                    logging.exception('Permission Denied')
                    
                try:
                    # ban user by removing them from mod group
                    group = Group.objects.get(name='mod')
                    group.user_set.remove(user)
                except:
                    logging.exception('Permission Denied')
    context = {'posts':posts}
    return render(request,'auth_app/main/home.html',context)



@login_required(login_url='/login')
@permission_required("auth_app.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('/home')
    else:
        form = PostForm()
    context = {'form':form}
    return render(request,'auth_app/main/create_post.html',context)


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
        
    context ={'form':form}
    return render(request,'registration/sign_up.html',context)

def logout_user(request):
    """ Handles user logout flow 
    Removes the authenticated user's ID from the request and deletes their session data.
    """
    logout(request)
    # request.user == Anonymous user
    return redirect("/login")