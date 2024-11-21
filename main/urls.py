from django.urls import path
from .views import *

urlpatterns = [
    path('', PostsList.as_view(), name= 'Posts_list'),
    path('<int:pk>/', PostDetail.as_view(), name='Post_detail'),
    path('search/', PostsSearch.as_view(), name= 'Posts_search'),
    path('create/', PostCreate.as_view(), name='Post_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='Post_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='Post_delete'),
    path('categories/', CategoryList.as_view(), name='Category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
    path('categories/<int:pk>/unsubscribe', unsubscribe, name='unsubscribe'),
    path('categories/<int:pk>/',CategoryDetail.as_view(),name='Category'),
    path('<int:pk>/comment',add_comment, name='add_comment'),
    path('my_comments/', user_comments, name='user_comments'),
    path('delete_comment/', delete_comment, name='delete_comment'),
    path('accept_comment/', accept_comment, name='accept_comment'),
]