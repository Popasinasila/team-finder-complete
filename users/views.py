from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from projects.utils import paginate_queryset

from .forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileEditForm,
    RegistrationForm,
)
from .models import User

FILTER_FAVORITES_AUTHORS = "favorites_authors"
FILTER_MY_PROJECT_PARTICIPANTS = "my_project_participants"
FILTER_USERS_WHO_LIKE_MY_PROJECTS = "users_who_like_my_projects"
FILTER_JOINED_AUTHORS = "joined_authors"


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("project_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно! Войдите в систему.")
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """User login view using email + password."""
    if request.user.is_authenticated:
        return redirect("project_list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "project_list")
                return redirect(next_url)
            messages.error(request, "Неверный email или пароль")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """User logout view."""
    logout(request)
    return redirect("project_list")


def profile(request, pk):
    """Public user profile page showing their projects."""
    profile_user = get_object_or_404(User, pk=pk)
    projects = profile_user.projects.select_related("author").all()
    return render(
        request,
        "users/profile.html",
        {"profile_user": profile_user, "projects": projects},
    )


@login_required
def edit_profile(request):
    """Edit own profile view."""
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("profile", pk=request.user.pk)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


def users_list(request):
    """Paginated list of users with optional filtering (Variant 1)."""
    active_filter = request.GET.get("filter", "")
    qs = User.objects.all()

    if request.user.is_authenticated and active_filter:
        user = request.user

        if active_filter == FILTER_FAVORITES_AUTHORS:
            qs = User.objects.filter(projects__favorited_by__user=user).distinct()

        elif active_filter == FILTER_MY_PROJECT_PARTICIPANTS:
            qs = User.objects.filter(joined_projects__author=user).exclude(pk=user.pk).distinct()

        elif active_filter == FILTER_USERS_WHO_LIKE_MY_PROJECTS:
            qs = User.objects.filter(favorites__project__author=user).exclude(pk=user.pk).distinct()

        elif active_filter == FILTER_JOINED_AUTHORS:
            qs = User.objects.filter(projects__participants=user).exclude(pk=user.pk).distinct()

    qs = qs.order_by("-date_joined")
    page_obj = paginate_queryset(qs, request.GET.get("page"))

    return render(
        request,
        "users/users_list.html",
        {"page_obj": page_obj, "active_filter": active_filter},
    )


@login_required
def change_password(request):
    """Change password view."""
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменён")
            return redirect("profile", pk=request.user.pk)
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})
