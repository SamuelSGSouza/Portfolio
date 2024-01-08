from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

class LoginView(TemplateView):
    template_name = 'auth/login.html'
    title = 'Login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.POST['user']
        password = request.POST['password']

        user = authenticate(request, username=user, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'telegram/dashboard.html')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, self.template_name)
        
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('login_view')

