from django.urls import path
from . import views

app_name = 'productivity'

urlpatterns = [
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('api/events/', views.events_api, name='events_api'),
    path('activity/add/', views.ActivityCreateView.as_view(), name='activity_add'),
    path('activity/<int:pk>/edit/', views.ActivityUpdateView.as_view(), name='activity_edit'),
    path('activity/<int:pk>/score/', views.score_activity, name='activity_score'),
    path('reports/user/<int:user_id>/', views.user_report, name='user_report'),
    path('activity/form-ajax/', views.activity_form_ajax, name='activity_form_ajax'),
]