from django.contrib.auth.models import User
from addons.accounts.models import Profile, Members

def find_left(member, member1):
    # member.child_id.profile will give profile object 
    # member.child. here you can pass User models filed 
    return member if member.child_id.profile.placement_type == "L" else member


def find_right(member, member1):
    # member.child_id.profile will give profile object 
    # member.child. here you can pass User models filed
    return member if member.child_id.profile.placement_type == "R" else member


def left_child(members):
    # child_member = find_left(members)
    #  abobe line will raise error for find take exactly 2 argument 1 given , need to correct
    #  here you need to iterate over members list it could be n list 
    child_member = find_left(members,'members')
    #  just took string to check
    return load_users(child_member.child_id)


def right_child(members):
    # child_member = find_left(members)
    #  abobe line will raise error for find take exactly 2 argument 1 given , need to correct
    #  here you need to iterate over members list it could be n list
    child_member = find_right(members,'members')
    #  just took string to check
    return load_users(child_member.child_id)


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
    members = Members.objects.filter(parent_id=user.id)
    # memebers is list of child , right now i am passing only 1 member in each left or right
    if members:
        return {
            'left' : left_child(members[0]),
            'right' : right_child(members[0]),
            'user': user_details
        
        }
    else:
        return {
            'user':user_details
        }