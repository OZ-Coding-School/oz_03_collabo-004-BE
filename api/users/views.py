# for admin user, added views.py
from django.contrib.auth.views import LoginView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .forms import AdminLoginForm

@method_decorator(staff_member_required, name='dispatch')
class AdminLoginView(LoginView):
    template_name = 'admin/login.html'
    form_class = AdminLoginForm
