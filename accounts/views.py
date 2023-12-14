from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from allauth.account.utils import complete_signup

from .forms import CustomSignupForm
