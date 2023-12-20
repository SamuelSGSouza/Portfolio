from django.shortcuts import render
from django.views.generic import TemplateView
from .functions import Cleaning
from django.http import HttpResponse
import os

class PageView(TemplateView):
    template_name = 'page.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

class HomePageView(PageView):
    template_name = 'index.html'
    title = 'Dashboard'
    

class DataCleaningView(PageView):
    template_name = 'data_analytcs/data_cleanning.html'
    title = 'Data Cleaning'

class ShowCleanedDataView(PageView):
    template_name = 'data_analytcs/show_cleaned_data.html'
    title = 'Show Cleaned Data'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        #verifica se o arquivo tem menos de 5mb
        if self.request.FILES['file_selected'].size > 5000000:
            context['error'] = 'File size is too large, please select a file with less than 5mb'
            return context

        cleaning = Cleaning(file=self.request.FILES['file_selected'], 
                            filename=self.request.FILES['file_selected'].name,
                            handle_null_values=self.request.POST.get('handle_null'),
                            handle_outliers=self.request.POST.get('handle_outliers'),
                            handle_duplicates=self.request.POST.get('handle_duplicates'),
                            handle_reescale=self.request.POST.get('handle_reescale'),
                            )
        df, success, failures, filepath = cleaning.main()
        self.request.session['file_path'] = filepath

        context['columns'] = df.columns.to_list()
        context['data'] = df.values.tolist()
        context['success'] = success
        context['failures'] = failures

        return context
    
    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
def download_file(request):
    file_path = request.session['file_path']
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    

#error 404
def error_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)