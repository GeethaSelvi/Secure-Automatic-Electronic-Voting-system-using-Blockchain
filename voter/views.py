from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import VoterLoginForm, ForgotPasswordForm
from .models import Voter, Results
from django.contrib import messages
import uuid
from adminapp.models import Candidate
from voting import settings
import logging
logger = logging.getLogger(__name__)

from django.db.models import Q
from web3 import Web3

def voter_signin(request):
    if request.method == 'POST':
        form = VoterLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                voter = Voter.objects.get(Q(email=username) | Q(eth_address=username))
                if not voter.check_password(password):
                    raise Voter.DoesNotExist
                if Results.objects.filter(voter=voter).exists():
                    messages.error(request, "You have already voted and cannot log in again. IF YOU TRY TO VOTE AGAIN LEGAL ACTION WILL BE TAKEN")
                    return redirect('voter_signin')
                request.session['voter_id'] = voter.id
                return redirect('candidates_info_list')
            except Voter.DoesNotExist:
                messages.error(request, "Invalid Email or Ethereum Address and password.")
    else:
        form = VoterLoginForm()
    return render(request, 'voter_signin.html', {'form': form})

def candidates_info_list(request):
    candidates = Candidate.objects.all()
    return render(request, 'candidates_info_list.html', {'candidates': candidates})

import json
# vo/voting/voter/views.py
def voting_page(request):
    if 'voter_id' not in request.session:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('voter_signin')
    
    try:
        contract = get_contract()
        candidate_count = contract.functions.candidateCount().call()
        candidates = []
        
        for i in range(1, candidate_count + 1):
            try:
                blockchain_candidate = contract.functions.getCandidate(i).call()
                db_candidate = Candidate.objects.filter(blockchain_id=i).first()
                if not db_candidate:
                    logger.warning(f"No DB candidate found for blockchain ID {i}")
                    continue
                candidates.append({
                    'id': blockchain_candidate[0],
                    'name': blockchain_candidate[1],
                    'party': blockchain_candidate[2],
                    'votes': blockchain_candidate[3],
                    'image_url': db_candidate.image.url,
                    'symbol_url': db_candidate.symbol_image.url
                 })

            except Exception as e:
                logger.error(f"Error processing candidate {i}: {str(e)}")
                continue

                
            except Candidate.DoesNotExist:
                logger.warning(f"Missing database entry for blockchain candidate ID {i}")
                continue
            except Exception as e:
                logger.error(f"Error processing candidate {i}: {str(e)}")
                continue
        
    except Exception as e:
        logger.error(f"Blockchain connection error: {str(e)}")
        messages.error(request, "Failed to connect to voting system. Please try again later.")
        return redirect('voter_dashboard')
    
    return render(request, 'voter.html', {
        'candidates': candidates,
        'contract_address': settings.CONTRACT_ADDRESS,
        'contract_abi_json': json.dumps(settings.CONTRACT_ABI)
    })


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                voter = Voter.objects.get(email=email)
                # Generate a new unique password in the format #123456#
                new_password = f"#{str(uuid.uuid4().int)[:6]}#"
                voter.password = new_password
                voter.save()
                # Send email with Aadhaar No. and new password
                send_mail(
                    'Password Reset',
                    f'Your Aadhaar No. is: {voter.aadhaar_no} and your new password is: {new_password}.',
                    'your email',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "Your Aadhaar No. and new password have been sent to your email.")
                return redirect('voter_signin')
            except Voter.DoesNotExist:
                messages.error(request, "No account found with this email.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})







# vo/voting/voter/views.py
from .blockchain import get_contract, get_web3
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse




from web3.exceptions import ContractLogicError
from web3.exceptions import ContractLogicError

from django.utils import timezone
from web3.exceptions import ContractLogicError

def submit_vote(request):
    if request.method == 'POST':
        candidate_id = int(request.POST.get('candidate_id'))
        voter_id = request.session.get('voter_id')
        
        try:
            voter = Voter.objects.get(id=voter_id)
            candidate = Candidate.objects.get(id=candidate_id)
            contract = get_contract()
            w3 = get_web3()
            
            # Check voting period
            current_time = int(timezone.now().timestamp())
            voting_start = contract.functions.votingStart().call()
            voting_end = contract.functions.votingEnd().call()
            
            if voting_start == 0 or voting_end == 0:
                return JsonResponse({'status': 'error', 'message': 'Voting period not set'})
                
            if current_time < voting_start:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Voting starts at {timezone.datetime.fromtimestamp(voting_start).strftime("%Y-%m-%d %H:%M")}'
                })
                
            if current_time > voting_end:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Voting ended at {timezone.datetime.fromtimestamp(voting_end).strftime("%Y-%m-%d %H:%M")}'
                })

            # Build transaction with proper gas estimation
            tx = contract.functions.vote(candidate.blockchain_id).build_transaction({
                'chainId': 1337,
                'nonce': w3.eth.get_transaction_count(voter.eth_address),
                'gas': 500000,
                'gasPrice': w3.to_wei('20', 'gwei')
            })
            
            signed_tx = w3.eth.account.sign_transaction(tx, voter.eth_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                candidate = Candidate.objects.get(blockchain_id=candidate_id)
                Results.objects.create(voter=voter, candidate=candidate, tx_hash=tx_hash.hex(),voted_at=timezone.now())
                return JsonResponse({'status': 'success', 'tx_hash': tx_hash.hex()})
            
            return JsonResponse({'status': 'error', 'message': 'Transaction reverted'})
            
        except ContractLogicError as e:
            error_message = str(e).split("reverted: ")[-1]
            return JsonResponse({'status': 'error', 'message': error_message})
        except Voter.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Voter not found'})
        except Candidate.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid candidate'})
        except Exception as e:
            logger.error(f"Voting error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Voting failed'})
    
    return redirect('voter_dashboard')





def voter_logout(request):
    if 'voter_id' in request.session:
        del request.session['voter_id']
    return redirect('voter_signin')



def voting_results(request):
    results = Results.objects.all()
    return render(request, 'voting_results.html', {'results': results})



def voter_dashboard(request):
    if 'voter_id' not in request.session:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('voter_signin')
    return render(request, 'voter_dashboard.html')

