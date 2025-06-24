from django.db import models
import uuid
from django.core.validators import MinLengthValidator

# vo/voting/voter/models.py
from django.contrib.auth.hashers import make_password, check_password
class Voter(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    aadhaar_no = models.CharField(max_length=12, unique=True, editable=False)  # Unique Aadhaar No.
    password = models.CharField(max_length=128, editable=False)   # Unique password
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    region = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    current_place = models.CharField(max_length=100)
    eth_address = models.CharField(max_length=42, unique=True)
    eth_private_key = models.CharField(max_length=66, editable=False)
    
    def get_web3_account(self):
        from web3 import Web3
        return Web3().eth.account.from_key(self.eth_private_key)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

# vo/voting/voter/models.py
class Results(models.Model):
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE)
    candidate = models.ForeignKey('adminapp.Candidate', on_delete=models.CASCADE)
    tx_hash = models.CharField(max_length=66)  # Blockchain transaction hash
    voted_at = models.DateTimeField(auto_now_add=True)

