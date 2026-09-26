import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from .forms_auth import (
    UserRegisterForm,
    RegistrationOTPVerifyForm,
    UserLoginForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm
)


def user_register(request):
    """Step 1: Takes user input & role, stores in session, prints OTP to terminal."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            otp = f"{random.randint(100000, 999999)}"

            # Hold data in session until OTP verification
            request.session['pending_registration'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'role': form.cleaned_data['role'],
                'password': form.cleaned_data['password'],
            }
            request.session['reg_otp'] = otp

            # Prominent terminal dispatch banner
            print("\n" + "=" * 70)
            print(f" [STOCKSENSE REGISTRATION OTP] New user: {form.cleaned_data['username']}")
            print(f" Assigned Role: {dict(UserProfile.ROLE_CHOICES).get(form.cleaned_data['role'])}")
            print(f" >>> ACTIVATION CODE IS:  {otp}  <<<")
            print("=" * 70 + "\n")

            messages.info(request, "Activation code sent! Check your terminal console.")
            return redirect('register_verify')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


def register_verify(request):
    """Step 2: Prompts for OTP. If valid, creates User and UserProfile with role."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    pending = request.session.get('pending_registration')
    session_otp = request.session.get('reg_otp')

    if not pending or not session_otp:
        messages.error(request, "Registration session expired. Please start over.")
        return redirect('register')

    if request.method == 'POST':
        form = RegistrationOTPVerifyForm(request.POST)
        if form.is_valid():
            submitted_otp = form.cleaned_data['otp'].strip()
            if submitted_otp == session_otp:
                # Create user in SQLite
                user = User.objects.create_user(
                    username=pending['username'],
                    email=pending['email'],
                    password=pending['password']
                )

                # Set chosen role
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = pending['role']
                profile.save()

                del request.session['pending_registration']
                del request.session['reg_otp']

                login(request, user)
                messages.success(request, f"Account activated! Welcome, {profile.get_role_display()}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid OTP code. Please check your terminal.")
    else:
        form = RegistrationOTPVerifyForm()

    return render(request, 'register_verify.html', {
        'form': form,
        'username': pending['username'],
        'role_name': dict(UserProfile.ROLE_CHOICES).get(pending['role'])
    })


def register_resend_otp(request):
    pending = request.session.get('pending_registration')
    if not pending:
        messages.error(request, "No active registration found. Please register again.")
        return redirect('register')

    new_otp = f"{random.randint(100000, 999999)}"
    request.session['reg_otp'] = new_otp

    print("\n" + "=" * 70)
    print(f" [STOCKSENSE RESENT OTP] User: {pending['username']}")
    print(f" >>> NEW CODE IS:  {new_otp}  <<<")
    print("=" * 70 + "\n")

    messages.info(request, "New OTP dispatched to your terminal.")
    return redirect('register_verify')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('index')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username_or_email']
            user = User.objects.filter(username=identifier).first() or User.objects.filter(email=identifier).first()

            if user:
                otp = f"{random.randint(100000, 999999)}"
                request.session['reset_otp'] = otp
                request.session['reset_user_id'] = user.id

                print("\n" + "=" * 65)
                print(f" [STOCKSENSE RESET OTP] Code for {user.username}: {otp}")
                print("=" * 65 + "\n")

                messages.info(request, "OTP sent! Check your terminal console.")
                return redirect('password_reset_confirm')
            else:
                messages.error(request, "No user account was found with those credentials.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'forgot_password.html', {'form': form})


def password_reset_confirm(request):
    if 'reset_otp' not in request.session or 'reset_user_id' not in request.session:
        messages.error(request, "Password reset session expired. Please request a new OTP.")
        return redirect('password_reset_request')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            submitted_otp = form.cleaned_data['otp'].strip()
            session_otp = request.session.get('reset_otp')

            if submitted_otp == session_otp:
                user = User.objects.get(id=request.session['reset_user_id'])
                user.set_password(form.cleaned_data['new_password'])
                user.save()

                del request.session['reset_otp']
                del request.session['reset_user_id']

                messages.success(request, "Password reset successfully! Please sign in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP code entered. Please check terminal.")
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'reset_password.html', {'form': form})