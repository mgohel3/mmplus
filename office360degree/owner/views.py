import pandas as pd
import json
from io import TextIOWrapper
from django.contrib.auth import authenticate, login, logout  # Add the missing import
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Sum, Min, Avg, Count
from .models import CustomUser, Company, SBU, BusinessCategory, Client,ContactPage, AboutUs, Zone, Schedule
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import LoginForm, UserCreationForm, ExtendedUserCreationForm, ProfileForm, BulkUserUploadForm, ClientUpdateForm, AddCategoryForm, ContactPageForm, AboutUsForm, ZoneForm, ScheduleForm
from django.views.decorators.csrf import csrf_protect
from itertools import chain
from datetime import datetime
from django.contrib import messages
from operator import itemgetter
from calendar import month_name
from django.http import JsonResponse


class SignUpView(CreateView):
    model = CustomUser
    template_name = 'registration/signup.html'
    fields = ['username', 'email', 'password']
    success_url = reverse_lazy('login')


def home(request):
    return render(request, 'owner/home.html')

@login_required
def dashboard_view(request):
    user = request.user

    if user.is_owner or user.is_hr:
        # For owners and HR, get the company directly from the user's company field
        company = user.company
        users_list = company.users.all()  # All users for owners and HR

    elif user.is_manager:
        # For managers, get the company based on their association with the manager field
        company = user.company
        # Get the team leads under this manager and their managed team members

    elif user.is_team_leader:
        # For team leaders, get the team members under this team leader
        company = user.company
        team_members = CustomUser.objects.filter(is_employee=True, team_leader=user)
        users_list = team_members
        # Calculate the survey participation rate for assigned users
        total_users_count = team_members.count()

    else:
        # For other user roles, handle the logic based on your application requirements
        # This could include checking relationships with other models or a default company
        company = user.company
        users_list = []

    context = {
        'user': user,
        'company': company,
        'users_list': users_list,  # Pass the users_list to the template
    }

    return render(request, 'owner/dashboard.html', context)


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('owner:dashboard')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
@login_required()
def survey_view(request):
    return render(request, 'owner/survey.html')

@login_required()
def survey_ees_view(request):
    return render(request, 'owner/survey.html')

@login_required()
def survey_es_view(request):
    return render(request, 'owner/survey.html')

@login_required()
def survey_os_view(request):
    return render(request, 'owner/survey.html')

@login_required()
def survey_cs_view(request):
    return render(request, 'owner/survey.html')
@login_required
def reports_view(request):
    # Fetch company information for the logged-in user
    user = request.user
    company = user.company

    # Fetch unique months from UserScore model
    months = UserScore.objects.dates('timestamp', 'month').distinct()

    # Prepare the data for heatmap
    heatmap_data = []
    for month in months:
        # Calculate engagement score for the current month
        total_achieved_score_month = \
            UserScore.objects.filter(timestamp__month=month.month, timestamp__year=month.year, score__gte=0).aggregate(
                Avg('score'))['score__avg'] or 0
        total_highest_score_month = UserScore.objects.filter(timestamp__month=month.month, timestamp__year=month.year,
                                                              score__gte=0).count() * 10  # Assuming a 10-point scale
        engagement_score_month = 0 if total_highest_score_month == 0 else round(
            (total_achieved_score_month / total_highest_score_month) * 10)

        # Append the engagement score data for the current month
        heatmap_data.append({'x': 'Engagement Score', 'y': month.strftime('%B'), 'value': engagement_score_month})

    # Extract unique months for Y axis
    yCategories = [month.strftime('%B') for month in months]

    # Pass the heatmap data and category names to the template
    context = {
        'heatmap_data': json.dumps(heatmap_data),
        'xCategories': json.dumps(['Engagement Score']),
        'yCategories': json.dumps(yCategories)
    }

    # Render your template with heatmap_data and categories
    return render(request, 'owner/reports.html', context)

@login_required()
def comments_view(request):
    return render(request, 'owner/comments.html')

@login_required()
def team_view(request):
    user = request.user
    company = user.company

    if user.is_owner or user.is_hr:
        users_list = company.users.all()
    elif user.is_manager:
        team_leads = CustomUser.objects.filter(is_team_leader=True, manager=user)
        team_members = CustomUser.objects.filter(is_employee=True, team_leader__in=team_leads)
        users_list = list(team_leads) + list(team_members)
    elif user.is_team_leader:
        team_members = CustomUser.objects.filter(is_employee=True, team_leader=user)
        users_list = team_members
    else:
        # Handle other user roles or set users_list to an empty list
        users_list = []

    context = {
        'user': user,
        'company': company,
        'users_list': users_list,
        'owner_count': company.users.filter(is_owner=True).count(),
        'hr_count': company.users.filter(is_hr=True).count(),
        'manager_count': CustomUser.objects.filter(is_manager=True, company=company).count(),
        'team_leader_count': CustomUser.objects.filter(is_team_leader=True, company=company).count(),
        'employee_count': CustomUser.objects.filter(is_employee=True, company=company).count(),
    }

    return render(request, 'owner/team.html', context)

@login_required()
def usermanagement_view(request):
    user = request.user

    if user.is_owner or user.is_hr:
        # For owners and HR, get the company directly from the user's company field
        company = user.company
        users_list = company.users.all()  # All users for owners and HR
    elif user.is_manager:
        # For managers, get the company based on their association with the manager field
        company = user.company
        # Get the team leads under this manager and their managed team members
        team_leads = CustomUser.objects.filter(is_team_leader=True, manager=user)
        team_members = CustomUser.objects.filter(is_employee=True, team_leader__in=team_leads)
        users_list = list(team_leads) + list(team_members)
    elif user.is_team_leader:
        # For team leaders, get the team members under this team leader
        company = user.company
        team_members = CustomUser.objects.filter(is_employee=True, team_leader=user)
        users_list = team_members
    else:
        # For other user roles, handle the logic based on your application requirements
        # This could include checking relationships with other models or a default company
        company = user.company
        users_list = []

    managers = CustomUser.objects.filter(is_manager=True)
    team_leaders = CustomUser.objects.filter(is_team_leader=True)
    hr_s = CustomUser.objects.filter(is_hr=True)
    employees = CustomUser.objects.filter(is_employee=True)
    sbu_units = SBU.objects.filter(company=user.company)

    add_user_form = ExtendedUserCreationForm()

    context = {
        'user': user,
        'company': company,
        'users_list': users_list,
        'add_user_form': add_user_form,
        'managers': managers,
        'team_leaders': team_leaders,
        'hr_s': hr_s,
        'employees': employees,
        'sbu_units': sbu_units,
    }

    return render(request, 'owner/user-managment.html', context)
@login_required
def profile(request):
    return render(request, 'owner/profile.html')

@login_required
def add_user(request):
    if not (request.user.is_authenticated and (request.user.is_owner or request.user.is_hr)):
        return redirect('dashboard')

    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            if form.cleaned_data['selected_role'] == 'custom':
                # If the selected role is 'Custom Role', use the custom role provided
                user.custom_role = form.cleaned_data['custom_role']
            else:
                # Set the corresponding role flag based on the selected role
                setattr(user, f'is_{form.cleaned_data["selected_role"]}', True)

            # Set manager, team leader, and HR based on the selected roles
            user.manager = form.cleaned_data['manager']
            user.team_leader = form.cleaned_data['team_leader']
            user.hr = form.cleaned_data['hr']

            # Assign the same company as the logged-in owner or HR
            user.company = request.user.company
            user.save()

            return redirect('owner:usermanagement')
        else:
            # Print form errors to the console for debugging
            print(form.errors)
    else:
        form = ExtendedUserCreationForm()

    return render(request, 'owner/user-management.html', {'form': form})

@login_required
def bulk_user_upload(request):
    if request.method == 'POST':
        bulk_upload_form = BulkUserUploadForm(request.POST, request.FILES)
        if bulk_upload_form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                try:
                    csv_data = TextIOWrapper(file, encoding='utf-8')
                    df = pd.read_csv(csv_data)

                    # Assuming the company is associated with the logged-in user
                    upload_user_company = request.user.company
                    print(f'Uploading users for company: {upload_user_company}')

                    for index, row in df.iterrows():
                        # Manually parse the date here
                        try:
                            joining_date = datetime.strptime(row['joining_date'], '%d-%m-%Y').date()
                        except ValueError:
                            messages.error(request,
                                           f'Error processing row {index + 1}: Invalid date format for joining_date.')
                            continue

                        # Set the common fields
                        row['joining_date'] = joining_date
                        row['company'] = upload_user_company.id  # Set the company for each user

                        # Fetch user IDs based on usernames
                        manager_username = row['manager']
                        team_leader_username = row['team_leader']
                        hr_username = row['hr']

                        # Retrieve the corresponding users from the database
                        manager_user = CustomUser.objects.filter(username=manager_username).first()
                        team_leader_user = CustomUser.objects.filter(username=team_leader_username).first()
                        hr_user = CustomUser.objects.filter(username=hr_username).first()

                        # Assign user objects or None if users are not found
                        row['manager'] = manager_user if manager_user else None
                        row['team_leader'] = team_leader_user if team_leader_user else None
                        row['hr'] = hr_user if hr_user else None

                        form = ExtendedUserCreationForm(row.to_dict())

                        if form.is_valid():
                            user = form.save(commit=False)
                            user.set_password(row['password'])
                            user.company = upload_user_company  # Set the company for the user
                            # Additional logic if needed
                            try:
                                user.save()
                                print(f'User created: {user.username}')
                            except Exception as e:
                                messages.error(request, f'Error saving user {user.username}: {str(e)}')
                                print(f'Error saving user {user.username}: {str(e)}')
                        else:
                            messages.error(request, f'Error processing row {index + 1}: {form.errors}')
                            print(f'Error processing row {index + 1}: {form.errors}')

                    messages.success(request, 'Bulk users added successfully!')
                    return redirect('owner:usermanagement')
                except pd.errors.EmptyDataError:
                    messages.error(request, 'Empty CSV file. Please upload a valid CSV file.')
                except Exception as e:
                    messages.error(request, f'An error occurred: {str(e)}')
                    print(f'Error: {str(e)}')
            else:
                messages.error(request, 'Invalid file format. Please upload a CSV file.')
        else:
            messages.error(request, 'Error uploading bulk users. Please check the form.')
    else:
        bulk_upload_form = BulkUserUploadForm()

    return render(request, 'owner/bulk_user_upload.html', {'bulk_upload_form': bulk_upload_form})

@login_required
def my_team_view(request):
    user = request.user

    if user.is_owner or user.is_hr:
        # For owners and HR, get the company directly from the user's company field
        company = user.company
        users_list = company.users.all()  # All users for owners and HR
    elif user.is_manager:
        # For managers, get the company based on their association with the manager field
        company = user.company
        # Get the team leads under this manager and their managed team members
        team_leads = CustomUser.objects.filter(is_team_leader=True, manager=user)
        team_members = CustomUser.objects.filter(is_employee=True, team_leader__in=team_leads)
        users_list = list(team_leads) + list(team_members)
    elif user.is_team_leader:
        # For team leaders, get the team members under this team leader
        company = user.company
        team_members = CustomUser.objects.filter(is_employee=True, team_leader=user)
        users_list = team_members
    else:
        # For other user roles, handle the logic based on your application requirements
        # This could include checking relationships with other models or a default company
        company = user.company
        users_list = []

    context = {
        'user': user,
        'company': company,
        'users_list': users_list,  # Pass the users_list to the template
    }

    return render(request, 'owner/my-team.html', context)

@login_required()
def account_settings_view(request):

    user = get_object_or_404(CustomUser, id=request.user.id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('owner:account_settings')
        else:
            print(form.errors)  # Add this line for debugging
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileForm(instance=user)
        form.fields['company'].queryset = Company.objects.filter(id=user.company.id)
        form.fields['sbu_units'].queryset = SBU.objects.filter(company=user.company)

    return render(request, 'owner/account_settings.html', {'form': form})

@login_required
def ac_survey_questions_view(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")

    if request.method == 'POST':
        form = SurveyForm(request.POST, user=user)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.creator = request.user
            survey.save()

            # Get selected questions from the form
            selected_question_ids = request.POST.getlist('selected_questions')
            selected_questions = SurveyQuestion.objects.filter(id__in=selected_question_ids)

            # Associate selected questions with the survey
            survey.questions.set(selected_questions)

            return redirect('owner:ac_survey_questions')  # Redirect to the survey questions view or another appropriate page
    else:
        form = SurveyForm(user=user, initial={'company': user.company})

    # Provide the list of available questions to the template
    questions = SurveyQuestion.objects.all()

    context = {
        'form': form,
        'questions': questions,
    }

    return render(request, 'owner/ac_survey_questions.html', context)

@login_required
def puls_survey_frequency_view(request):
    return render(request, 'owner/puls_survey_frequency.html')

@login_required()
def custom_survey_launch_view(request):
    return render(request, 'owner/custom_survey_launch.html')

@login_required()
def notifications_view(request):
    return render(request, 'owner/notifications.html')

@login_required()
def app_integration_view(request):
    return render(request, 'owner/app_integration.html')

def logout_view(request):
    logout(request)
    return redirect('owner:login')

@login_required
def profile_view(request):
    user = get_object_or_404(CustomUser, id=request.user.id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('owner:account_settings')
        else:
            print(form.errors)  # Add this line for debugging
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'owner/a_s_content.html', {'form': form})

@login_required()
def dhome_view(request):
    return render(request, 'owner/dhome.html')
@login_required
def dabout_view(request):
    # Fetch the first (or only) AboutUs instance
    about_us = AboutUs.objects.first()

    if request.method == 'POST':
        form = AboutUsForm(request.POST, request.FILES, instance=about_us)
        if form.is_valid():
            form.save()
            return redirect('owner:dabout')  # Redirect to the 'dabout' page after saving
    else:
        form = AboutUsForm(instance=about_us)

    return render(request, 'owner/dabout.html', {'form': form})

@login_required
def dclients_view(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            category_name = request.POST.get('name')
            category, created = BusinessCategory.objects.get_or_create(name=category_name)
            if created:
                return JsonResponse({'success': True, 'id': category.id})
            else:
                return JsonResponse({'success': False, 'error': 'Category already exists.'})
        else:
            form = ClientUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('owner:dclients')  # Replace 'owner:dclients' with the actual URL
    else:
        form = ClientUpdateForm()

        category_form = AddCategoryForm()

    return render(request, 'owner/dclients.html', {'form': form, 'category_form': category_form})
@login_required
def dclients_viewall_view(request):
    clients_list = Client.objects.all()  # Fetch all clients
    return render(request, 'owner/dclients_viewall.html', {'clients_list': clients_list})
@login_required
def dclients_viewall_content_view(request):
    clients_list = Client.objects.all()  # Fetch all clients
    return render(request, 'owner/dclients_viewall_content.html')
@login_required
def dclients_content_view(request):
    clients = Client.objects.all()  # Fetch all clients
    return render(request, 'owner/dclients_content.html')
@login_required
def dcontact_view(request):
    contact_page = ContactPage.objects.first()  # Fetch the first (or only) ContactPage instance

    if request.method == 'POST':
        form = ContactPageForm(request.POST, request.FILES, instance=contact_page)
        if form.is_valid():
            form.save()
            return redirect('owner:dcontact')  # Redirect to your original 'dcontact' page after saving
    else:
        form = ContactPageForm(instance=contact_page)

    return render(request, 'owner/dcontact.html', {'form': form})

@login_required
def depaper_view(request):
    return render(request, 'owner/depaper.html')

@login_required
def depaperpricing_view(request):
    return render(request, 'owner/depaperpricing.html')

@login_required
def dinquiry_view(request):
    return render(request, 'owner/dinquiry.html')

@login_required
def dnotification_view(request):
    return render(request, 'owner/dnotification.html')

@login_required
def dschedule_view(request):
    # Fetch all existing schedules
    schedules = Schedule.objects.all()

    if request.method == 'POST':
        # Handle form submission to create a new schedule
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            # Auto-populate day_of_week based on publish_date
            selected_date = form.cleaned_data['publish_date']
            schedule.day_of_week = selected_date.strftime('%A')  # Get the day name
            schedule.save()
            return redirect('dschedule_view')  # Redirect to the same view after saving
    else:
        form = ScheduleForm()

    return render(request, 'owner/dschedule.html', {
        'schedules': schedules,
        'form': form,
    })

def schedule_delete(request, pk):
    # Handle schedule deletion
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def dscheduleads_view(request):
    return render(request, 'owner/dscheduleads.html')

@login_required
def depaperads_view(request):
    return render(request, 'owner/depaperads.html')

@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('name')
        category, created = BusinessCategory.objects.get_or_create(name=category_name)
        if created:
            return JsonResponse({'success': True, 'id': category.id})
        else:
            return JsonResponse({'success': False, 'error': 'Category already exists.'})

@login_required
def add_zone(request):
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('zone_list')  # Redirect to a zone list page
    else:
        form = ZoneForm()
    return render(request, 'admin/add_zone.html', {'form': form})

@login_required
def zone_list(request):
    zones = Zone.objects.all()
    return render(request, 'admin/zone_list.html', {'zones': zones})

@login_required
def delete_zone(request, zone_id):
    zone = Zone.objects.get(id=zone_id)
    zone.delete()
    return redirect('zone_list')
