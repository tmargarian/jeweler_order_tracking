# Handling sign up signals to create Owner & UserProfile instances
# immediately after sign up
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model

from .models import UserProfile, Company, Owner


@receiver(user_signed_up)
def create_user_profile(sender, **kwargs):
    user_profile = UserProfile(user_id=kwargs["user"].id)
    user_profile.save()


@receiver(user_signed_up)
def create_owner(sender, **kwargs):
    owner = Owner(user_id=kwargs["user"].id)

    owner.save()


@receiver(user_signed_up)
def create_company(sender, **kwargs):
    company = Company()

    User = get_user_model()
    current_user = User.objects.get(id=kwargs["user"].id)
    owner = Owner.objects.get(user_id=kwargs["user"].id)

    company.owner_id = owner.id
    company.save()

    current_user.company_id = company.id
    owner.company_id = company.id
    current_user.save()
    owner.save()
