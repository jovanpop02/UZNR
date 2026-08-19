from django.urls import path

from . import views

urlpatterns = [
    path('announcements', views.AnnouncementListView.as_view(), name='announcement-list'),
    path('news', views.NewsListView.as_view(), name='news-list'),
    path('news/<slug:slug>', views.NewsDetailView.as_view(), name='news-detail'),
    path('members', views.MemberListView.as_view(), name='member-list'),
    path('important-links', views.ImportantLinkListView.as_view(), name='important-link-list'),
    path('pages/<slug:slug>', views.PageDetailView.as_view(), name='page-detail'),
    path('contact', views.ContactCreateView.as_view(), name='contact-create'),
]
