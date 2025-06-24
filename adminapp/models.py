from django.db import models
from voter.blockchain import get_contract

class Candidate(models.Model):
    blockchain_id = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    party_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    election_place = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    image = models.ImageField(upload_to='candidates/', null=True, blank=True)
    symbol_image = models.ImageField(upload_to='candidates/symbols/', null=True, blank=True)  # New field

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.blockchain_id:
            contract = get_contract()
            self.blockchain_id = contract.functions.candidateCount().call() + 1
        super().save(*args, **kwargs)
        
    def update_votes(self):
        contract = get_contract()
        _, _, _, votes = contract.functions.getCandidate(self.blockchain_id).call()
        self.votes = votes
        self.save()

import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=64)  # SHA-256 produces 64-character hash
    otp = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.username
    

class Schedule(models.Model):
    election_name = models.CharField(max_length=255)
    election_date = models.DateField()
    region = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.election_name
