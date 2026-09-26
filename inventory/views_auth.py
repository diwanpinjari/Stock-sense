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
    PasswordResetConfirmForm,
)


# =========================================================
# REGISTRATION
# =========================================================

def user_register(request):
    """
    Step 1:
    Collect registration information, store it temporarily
    in the session, generate an OTP, and display the OTP
    in the terminal.
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            otp = f"{random.randint(100000, 999999)}"

            # Store registration data temporarily in session.
            request.session["pending_registration"] = {
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "role": form.cleaned_data["role"],
                "password": form.cleaned_data["password"],
            }

            request.session["reg_otp"] = otp

            # Display OTP in terminal.
            print("\n" + "=" * 70)
            print(
                f" [STOCKSENSE REGISTRATION OTP] "
                f"New user: {form.cleaned_data['username']}"
            )
            print(
                f" Assigned Role: "
                f"{dict(UserProfile.ROLE_CHOICES).get(form.cleaned_data['role'])}"
            )
            print(f" >>> ACTIVATION CODE IS:  {otp}  <<<")
            print("=" * 70 + "\n")

            messages.info(
                request,
                "Activation code sent! Check your terminal console."
            )

            return redirect("register_verify")

    else:
        form = UserRegisterForm()

    return render(
        request,
        "register.html",
        {"form": form},
    )


# =========================================================
# REGISTRATION OTP VERIFICATION
# =========================================================

def register_verify(request):
    """
    Step 2:
    Verify the registration OTP.

    If the OTP is correct:
    - Create the Django User
    - Create/update UserProfile
    - Assign the selected role
    - Clear registration session
    - Clear old messages
    - Log the user in
    - Redirect to dashboard
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    pending = request.session.get("pending_registration")
    session_otp = request.session.get("reg_otp")

    # No active registration session.
    if not pending or not session_otp:
        messages.error(
            request,
            "Registration session expired. Please start over."
        )
        return redirect("register")

    if request.method == "POST":
        form = RegistrationOTPVerifyForm(request.POST)

        if form.is_valid():
            submitted_otp = form.cleaned_data["otp"].strip()

            # =================================================
            # CORRECT OTP
            # =================================================
            if submitted_otp == session_otp:

                # Create Django user.
                user = User.objects.create_user(
                    username=pending["username"],
                    email=pending["email"],
                    password=pending["password"],
                )

                # Create or retrieve user profile.
                profile, _ = UserProfile.objects.get_or_create(
                    user=user
                )

                # Assign selected role.
                profile.role = pending["role"]
                profile.save()

                # Clear registration session data.
                request.session.pop(
                    "pending_registration",
                    None,
                )
                request.session.pop(
                    "reg_otp",
                    None,
                )

                # =================================================
                # IMPORTANT:
                # Clear old Django flash messages.
                #
                # This prevents messages such as:
                # "Registration session expired..."
                # from appearing on the dashboard after
                # successful registration.
                # =================================================
                old_messages = messages.get_messages(request)
                list(old_messages)

                # Log the newly created user in.
                login(request, user)

                # Show only the current success message.
                messages.success(
                    request,
                    f"Account activated! Welcome, "
                    f"{profile.get_role_display()}.",
                )

                return redirect("dashboard")

            # =================================================
            # INCORRECT OTP
            # =================================================
            else:
                messages.error(
                    request,
                    "Invalid OTP code. Please check your terminal.",
                )

    else:
        form = RegistrationOTPVerifyForm()

    return render(
        request,
        "register_verify.html",
        {
            "form": form,
            "username": pending["username"],
            "role_name": dict(
                UserProfile.ROLE_CHOICES
            ).get(pending["role"]),
        },
    )


# =========================================================
# RESEND REGISTRATION OTP
# =========================================================

def register_resend_otp(request):
    """
    Generate and display a new registration OTP.
    """

    pending = request.session.get("pending_registration")

    if not pending:
        messages.error(
            request,
            "No active registration found. Please register again.",
        )
        return redirect("register")

    new_otp = f"{random.randint(100000, 999999)}"

    request.session["reg_otp"] = new_otp

    print("\n" + "=" * 70)
    print(
        f" [STOCKSENSE RESENT OTP] "
        f"User: {pending['username']}"
    )
    print(f" >>> NEW CODE IS:  {new_otp}  <<<")
    print("=" * 70 + "\n")

    messages.info(
        request,
        "New OTP dispatched to your terminal.",
    )

    return redirect("register_verify")


# =========================================================
# LOGIN
# =========================================================

def user_login(request):
    """
    Authenticate an existing user.
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user is not None:
                login(request, user)

                messages.success(
                    request,
                    f"Welcome back, {user.username}!",
                )

                return redirect("dashboard")

            messages.error(
                request,
                "Invalid username or password.",
            )

    else:
        form = UserLoginForm()

    return render(
        request,
        "login.html",
        {"form": form},
    )


# =========================================================
# LOGOUT
# =========================================================

def user_logout(request):
    """
    Log the current user out.
    """

    logout(request)

    messages.info(
        request,
        "You have been logged out.",
    )

    return redirect("index")


# =========================================================
# PASSWORD RESET - REQUEST OTP
# =========================================================

def password_reset_request(request):
    """
    Step 1 of password reset:
    Find the user and generate a reset OTP.
    """

    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            identifier = form.cleaned_data["username_or_email"]

            user = (
                User.objects.filter(
                    username=identifier
                ).first()
                or User.objects.filter(
                    email=identifier
                ).first()
            )

            if user:
                otp = f"{random.randint(100000, 999999)}"

                request.session["reset_otp"] = otp
                request.session["reset_user_id"] = user.id

                print("\n" + "=" * 65)
                print(
                    f" [STOCKSENSE RESET OTP] "
                    f"Code for {user.username}: {otp}"
                )
                print("=" * 65 + "\n")

                messages.info(
                    request,
                    "OTP sent! Check your terminal console.",
                )

                return redirect(
                    "reset_password"
                )

            messages.error(
                request,
                "No user account was found with those credentials.",
            )

    else:
        form = PasswordResetRequestForm()

    return render(
        request,
        "forgot_password.html",
        {"form": form},
    )


# =========================================================
# PASSWORD RESET - CONFIRM OTP + NEW PASSWORD
# =========================================================

def password_reset_confirm(request):
    """
    Step 2 of password reset:
    Verify OTP and set the new password.
    """

    if (
        "reset_otp" not in request.session
        or "reset_user_id" not in request.session
    ):
        messages.error(
            request,
            "Password reset session expired. "
            "Please request a new OTP.",
        )

        return redirect(
            "forgot_password"
        )

    if request.method == "POST":
        form = PasswordResetConfirmForm(request.POST)

        if form.is_valid():
            submitted_otp = form.cleaned_data["otp"].strip()
            session_otp = request.session.get("reset_otp")

            # =================================================
            # CORRECT RESET OTP
            # =================================================
            if submitted_otp == session_otp:

                try:
                    user = User.objects.get(
                        id=request.session["reset_user_id"]
                    )
                except User.DoesNotExist:
                    # Clean invalid reset session.
                    request.session.pop(
                        "reset_otp",
                        None,
                    )
                    request.session.pop(
                        "reset_user_id",
                        None,
                    )

                    messages.error(
                        request,
                        "The user account could not be found.",
                    )

                    return redirect("login")

                # Set new password.
                user.set_password(
                    form.cleaned_data["new_password"]
                )
                user.save()

                # Clear password reset session.
                request.session.pop(
                    "reset_otp",
                    None,
                )
                request.session.pop(
                    "reset_user_id",
                    None,
                )

                messages.success(
                    request,
                    "Password reset successfully! Please sign in.",
                )

                return redirect("login")

            # =================================================
            # INCORRECT RESET OTP
            # =================================================
            else:
                messages.error(
                    request,
                    "Invalid OTP code entered. "
                    "Please check terminal.",
                )

    else:
        form = PasswordResetConfirmForm()

    return render(
        request,
        "reset_password.html",
        {"form": form},
    )