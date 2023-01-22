from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import logout

from .forms import UserEditForm

@login_required
def dashboard(request):
    return render(request, 'account/user/dashboard.html')

@login_required
def edit_details(request):

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    context = {'user_form': user_form}

    return render(request, 'account/user/edit_details.html', context)

@login_required
def delete_user(request):
    user = User.objects.get(user_name=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('account:delete_confirmation')

