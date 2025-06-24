from django.utils.deprecation import MiddlewareMixin
from .blockchain import get_contract
from django.shortcuts import render, redirect

class VotingStatusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'voter_address' in request.session:
            contract = get_contract()
            has_voted = contract.functions.voters(
                request.session['voter_address']
            ).call()
            
            if has_voted:
                request.session.flush()
                return redirect('voter_signin')