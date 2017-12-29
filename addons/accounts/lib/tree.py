from django.contrib.auth.models import User
from addons.accounts.models import Profile

def find_left(mem1, mem2):
    return mem1 if mem1.placement_type == "L" else mem2


def find_right(mem1, mem2):
    return mem1 if mem1.placement_type == "R" else mem2


def left_child(members):
       child_member = find_left(members)
       return load_users(child_member)


def right_child(members):
       child_member = find_right(members)
       return load_users(child_member)


def load_users(user):
    profile = Profile.objects.get(user=user)
    user_details = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_auto_id": profile.user_auto_id,
        "sponsor_id": profile.sponser_id,
        "placement_id": profile.placement_id,
        "mobile": profile.mobile,
        "placement_position": profile.placement_position
    }
    if user.members:
         return {
         "user": user_details,
         "left": left_child(user.members),
         "right": right_child(user.members)
         }
    else:
         return {
         user: user.details
        }