from django.shortcuts import render, redirect, get_object_or_404
from .models import Candidate, AdminUser, Schedule
from voter.models import Voter, Results
from .forms import CandidateForm, VoterForm, AdminRegisterForm, AdminLoginForm, ScheduleForm
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random, string, uuid
from django.http import JsonResponse
from django.db import models  # Add this import
from .models import Schedule, Candidate
from voting import settings
from adminapp.models import hash_password
from web3 import Web3

from voter.blockchain import get_web3

# Candidate Management Views
from voter.blockchain import get_contract, get_web3
from web3.auto import w3
from eth_account import Account
import secrets


# Candidate Management Views
def candidate_list(request):
    candidates = Candidate.objects.all()
    return render(request, 'adminapp/candidate_list.html', {'candidates': candidates})

import logging

logger = logging.getLogger(__name__)
# vo/voting/adminapp/views.py



logger = logging.getLogger(__name__)


def add_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            
            try:
                w3 = get_web3()
                contract = get_contract()
                account = w3.eth.account.from_key(settings.PRIVATE_KEY)
                
                # Build transaction with proper parameters
                tx = contract.functions.addCandidate(
                    candidate.name,
                    candidate.party_name
                ).build_transaction({
                    'chainId': 1337,
                    'gas': 500000,
                    'gasPrice': w3.to_wei('20', 'gwei'),
                    'nonce': w3.eth.get_transaction_count(account.address),
                })

                # Sign transaction properly for web3 v7.10.0
                signed_tx = account.sign_transaction(tx)
                
                # Send raw transaction
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if receipt.status == 1:
                    candidate.blockchain_id = contract.functions.candidateCount().call()
                    candidate.save()
                    messages.success(request, 'Candidate added to blockchain!')
                else:
                    messages.error(request, 'Blockchain transaction failed')

            except Exception as e:
                logger.error(f"Blockchain error: {str(e)}", exc_info=True)
                messages.error(request, f'Error adding candidate: {str(e)}')
            
            return redirect('candidate_list')
    else:
        form = CandidateForm()
    return render(request, 'adminapp/add_candidate.html', {'form': form})


def update_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully.')
            return redirect('candidate_list')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'adminapp/update_candidate.html', {'form': form})

def delete_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        try:
            # Get blockchain connection
            w3 = get_web3()
            contract = get_contract()
            admin_account = w3.eth.account.from_key(settings.PRIVATE_KEY)
            
            # Build removal transaction
            tx = contract.functions.removeCandidate(
                candidate.blockchain_id
            ).build_transaction({
                'chainId': 1337,
                'nonce': w3.eth.get_transaction_count(admin_account.address),
                'gas': 500000,
                'gasPrice': w3.to_wei('20', 'gwei')
            })
            
            # Send transaction
            signed_tx = admin_account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                candidate.delete()
                messages.success(request, 'Candidate removed from both systems')
            else:
                messages.error(request, 'Blockchain removal failed')

        except Exception as e:
            logger.error(f"Deletion error: {str(e)}")
            messages.error(request, f'Deletion failed: {str(e)}')

        return redirect('candidate_list')
    return render(request, 'adminapp/delete_candidate.html', {'candidate': candidate})




def voter_list(request):
    voters = Voter.objects.all()
    return render(request, 'adminapp/voter_list.html', {'voters': voters})

# vo/voting/adminapp/views.py

# vo/voting/adminapp/views.py


def add_voter(request):
    if request.method == 'POST':
        form = VoterForm(request.POST)
        if form.is_valid():
            voter = form.save(commit=False)
            
            # Generate blockchain account
            w3 = get_web3()
            account = w3.eth.account.create()
            
            # Store credentials
            voter.aadhaar_no = str(uuid.uuid4().int)[:12]
            voter.eth_address = account.address
            voter.eth_private_key = account.key.hex()  # Corrected attribute name
            temp_password = f"#{str(uuid.uuid4().int)[:6]}#"
            voter.set_password(temp_password)
            
            voter.save()
            
            # Send credentials via email
            send_mail(
                'Your Voting Credentials',
                f'Ethereum Address: {account.address}\nPrivate Key: {account.key.hex()}\nTemp Password: {temp_password}',
                settings.DEFAULT_FROM_EMAIL,
                [voter.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Voter added with blockchain credentials')
            return redirect('voter_list')
        else:
            messages.error(request, 'Form is invalid. Please correct the errors.')
    else:
        form = VoterForm()
    
    return render(request, 'adminapp/add_voter.html', {'form': form})

    # ... rest of the function

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
def update_voter(request, pk):
    voter = get_object_or_404(Voter, pk=pk)
    original_email = voter.email  # Capture original email before any changes

    if request.method == 'POST':
        form = VoterForm(request.POST, instance=voter)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            email_changed = new_email != original_email

            try:
                if email_changed:
                    send_credentials_email(voter, new_email)
                    messages.success(request, 'Voter updated. Credentials sent to new email.')
                else:
                    messages.success(request, 'Voter updated successfully.')
                
                form.save()  # Save the form after sending email
                return redirect('voter_list')
            except Exception as e:
                messages.error(request, f'Error updating voter: {e}')
                return redirect('voter_list')
    else:
        form = VoterForm(instance=voter)

    return render(request, 'adminapp/update_voter.html', {'form': form})


def send_credentials_email(voter, new_email):
    subject = 'Updated Voting Credentials'
    message = (
        f'Dear {voter.name},\n\n'
        f'Your voting credentials have been updated. Please find your details below:\n\n'
        f'Aadhaar No.: {voter.aadhaar_no}\n'
        f'Password: {voter.password}\n\n'
        'Please use these credentials to vote.'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [new_email]

    sent = send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    if not sent:
        raise Exception('Failed to send credentials email')


def delete_voter(request, pk):
    voter = get_object_or_404(Voter, pk=pk)
    if request.method == 'POST':
        voter.delete()
        return redirect('voter_list')
    return render(request, 'adminapp/delete_voter.html', {'voter': voter})



def send_verification_code(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = AdminUser.objects.get(username=username)
            # Generate a 6-digit OTP
            otp = ''.join(random.choices('0123456789', k=6))
            # Save the OTP to the user (for verification later)
            user.otp = otp
            user.save()
            # Send the OTP via email
            send_mail(
                'Your Verification Code',
                f'Your verification code is: {otp}',
                'your email',
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except AdminUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



def admin_register(request):
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug: Print submitted data
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug: Check if form is valid
            # Save the new admin user
            AdminUser.objects.create(
                username=form.cleaned_data['username'],
                fullname=form.cleaned_data['fullname'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            messages.success(request, "Registration successful. Please login.")
            return redirect('admin_login')
        else:
            print("Form errors:", form.errors)  # Debug: Print form errors
    else:
        form = AdminRegisterForm()
    return render(request, 'adminapp/register.html', {'form': form})



def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = hash_password(form.cleaned_data['password'])
            verification_code = form.cleaned_data.get('verification_code')
            
            try:
                user = AdminUser.objects.get(username=username, password=password)
                if user.otp == verification_code:
                    messages.success(request, "Login successful.")
                    return redirect('candidate_list')
                else:
                    messages.error(request, "Valid verification code.")
            except AdminUser.DoesNotExist:
                messages.error(request, "Invalid credentials")
    else:
        form = AdminLoginForm()
    return render(request, 'adminapp/login.html', {'form': form})



def admin_logout(request):
    # Add any logout logic here (e.g., clearing sessions)
    return redirect('admin_login')



def forgot_pass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = AdminUser.objects.get(email=email)
            new_password_plain = f"#{''.join(random.choices('0123456789', k=6))}#"
            user.password = hash_password(new_password_plain)
            user.save()
            # Email plain text password to user
            send_mail(
                'Password Reset',
                f'New password: {new_password_plain}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "New password sent")
            return redirect('admin_login')
        except AdminUser.DoesNotExist:
            messages.error(request, "Email not found")
    return render(request, 'adminapp/forgot_pass.html')




def candidate_list(request):
    candidates = Candidate.objects.all()
    schedule = Schedule.objects.all()  # Fetch schedule data
    return render(request, 'adminapp/candidate_list.html', {'candidates': candidates, 'schedule': schedule})


def schedule_list(request):
    schedule = Schedule.objects.all()
    return render(request, 'adminapp/schedule_list.html', {'schedule': schedule})

from django.utils import timezone
import time

# In adminapp/views.py
from django.utils import timezone
import datetime

# adminapp/views.py
from django.utils import timezone
from datetime import datetime as dt, time
import time as t
# Correct imports at the top
from datetime import datetime, time  # Import classes directly
from datetime import datetime, time, timedelta
from .models import Schedule
from .forms import ScheduleForm
import logging

logger = logging.getLogger(__name__)
from datetime import datetime, time, timezone as dt_timezone  # Add this


def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            try:
                schedule = form.save()
                
                # Get current UTC time with buffer
                current_utc = datetime.now(dt_timezone.utc).timestamp()
                start_time = int(current_utc) + 15  # 15-second buffer
                end_time = start_time + 86400  # 24 hours

                # Rest of blockchain code remains unchanged
                w3 = get_web3()
                contract = get_contract()
                admin_account = w3.eth.account.from_key(settings.PRIVATE_KEY)
                
                tx = contract.functions.setVotingPeriod(start_time, end_time).build_transaction({
                    'chainId': 1337,
                    'nonce': w3.eth.get_transaction_count(admin_account.address),
                    'gas': 1000000,
                    'gasPrice': w3.to_wei('50', 'gwei')
                })
                
                signed_tx = admin_account.sign_transaction(tx)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                if receipt.status == 1:
                    messages.success(request, "Voting period set successfully!")
                else:
                    messages.error(request, "Blockchain transaction failed")

                return redirect('schedule_list')

            except Exception as e:
                logger.error(f"Error creating schedule: {str(e)}")
                messages.error(request, f"Error: {str(e)}")
                return render(request, 'adminapp/add_schedule.html', {'form': form})
    
    # Rest of the function remains unchanged

    else:
        form = ScheduleForm()
    
    return render(request, 'adminapp/add_schedule.html', {'form': form})


def update_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully.')
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'adminapp/update_schedule.html', {'form': form})

def delete_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully.')
        return redirect('schedule_list')
    return render(request, 'adminapp/delete_schedule.html', {'schedule': schedule})

# adminapp/views.py
from voter.blockchain import get_contract

# adminapp/views.py
from voter.blockchain import get_contract

def overall_results(request):
    try:
        contract = get_contract()
        candidate_count = contract.functions.candidateCount().call()
        candidates = []
        
        for i in range(1, candidate_count + 1):
            blockchain_candidate = contract.functions.getCandidate(i).call()
            try:
                db_candidate = Candidate.objects.get(blockchain_id=i)
                candidates.append({
                    'id': blockchain_candidate[0],
                    'name': blockchain_candidate[1],
                    'party_name': blockchain_candidate[2],
                    'votes': blockchain_candidate[3],  # Use 'votes' instead of 'total_votes'
                    'image': db_candidate.image,
                    'symbol_image': db_candidate.symbol_image
                })
            except Candidate.DoesNotExist:
                logger.warning(f"Missing database entry for candidate ID {i}")
                continue

        return render(request, 'adminapp/overall_results.html', {
            'candidates': candidates,
            'schedule': Schedule.objects.all()
        })
        
    except Exception as e:
        logger.error(f"Blockchain connection failed: {str(e)}")
        # Update database votes before showing
        candidates = Candidate.objects.all()
        for candidate in candidates:
            try:
                candidate.update_votes()
            except Exception as update_error:
                logger.error(f"Vote update failed for {candidate.name}: {str(update_error)}")
        
        return render(request, 'adminapp/overall_results.html', {
            'candidates': candidates,
            'error': 'Blockchain data unavailable',
            'schedule': Schedule.objects.all()
        })

# adminapp/views.py
from web3 import Web3

def sync_votes(request):
    contract = get_contract()
    candidates = Candidate.objects.all()
    
    for candidate in candidates:
        if candidate.blockchain_id:
            votes = contract.functions.getCandidate(candidate.blockchain_id).call()[3]
            candidate.votes = votes
            candidate.save()
    
    return redirect('adminapp:overall_results')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from voter.blockchain import get_contract, get_web3
from django.conf import settings
from datetime import datetime

@csrf_exempt
def initialize_voting_period(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        
        # Convert Django datetime to Unix timestamp
        start_time = int(schedule.election_date.timestamp())
        end_time = start_time + 86400  # 24 hours after start

        contract = get_contract()
        w3 = get_web3()
        
        try:
            # Use admin account to set dates
            admin_account = w3.eth.account.from_key(settings.PRIVATE_KEY)
            tx = contract.functions.setVotingPeriod(start_time, end_time).build_transaction({
                'chainId': 1337,
                'nonce': w3.eth.get_transaction_count(admin_account.address),
                'gas': 1000000,
                'gasPrice': w3.to_wei('20', 'gwei')
            })
            
            signed_tx = w3.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return JsonResponse({'status': 'success', 'tx_hash': tx_hash.hex()})
            else:
                return JsonResponse({'status': 'error', 'message': 'Transaction failed'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
