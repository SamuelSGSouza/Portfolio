from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    ### CLEANING DATA ###
    path('data_cleaning/', views.DataCleaningView.as_view(), name='data_cleaning'),
    path('show_cleaned_data/', views.ShowCleanedDataView.as_view(), name='show_cleaned_data'),
    path('download_file/', views.download_file, name='download_file'),

    ### DATA ANALYTICS ###
    path('data_analytics/', views.DataAnalyticsView.as_view(), name='data_analytics'),
    path('show_data_analytics/', views.ShowDataAnalyticsView.as_view(), name='show_data_analytics'),
]