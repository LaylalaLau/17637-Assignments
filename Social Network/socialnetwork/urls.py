from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('', views.global_stream_action, name='home'),
    path('global_stream', views.global_stream_action, name='global_stream'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('follower_stream', views.follower_stream_action, name='follower_stream'),
    path('profile', views.profile_action, name='profile'),
    path('other_profile/<int:id>', views.other_profile_action, name='other_profile'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('follow/<int:id>', views.follow, name='follow'),
    path('unfollow/<int:id>', views.unfollow, name='unfollow'),

    path('add-comment', views.add_comment, name='add-comment'),
    path('add-post', views.add_post, name='add-post'),
    path('get-global', views.get_list_json_dumps_serializer),
    path('get-follower', views.get_follower_stream)
]

