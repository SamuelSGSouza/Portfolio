from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('data_cleaning/', views.DataCleaningView.as_view(), name='data_cleaning'),
    path('show_cleaned_data/', views.ShowCleanedDataView.as_view(), name='show_cleaned_data'),
    path('download_file/', views.download_file, name='download_file'),
]