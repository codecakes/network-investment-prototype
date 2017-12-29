from django.contrib.auth.models import User
from addons.accounts.models import Profile, Members


def find_left(member1, member2):
    # member.child_id.profile will give profile object
    return member1 if member1.child_id.profile.placement_position == "L" else member2


def find_right(member1, member2):
    # member.child. here you can pass User models filed
    return member1 if member1.child_id.profile.placement_position == "R" else member2


def is_left(member):
    return member.child_id.profile.placement_position == "L"


def is_right(member):
    return member.child_id.profile.placement_position == "R"


def left_child(members):
    if len(members) == 0: return {}

    if len(members) > 1:
        child_member = getattr(find_left(*members), 'child_id')
    elif is_left(members[0]):
        child_member = getattr(members[0], 'child_id')
    else:
        child_member = None
    return load_users(child_member) if child_member else {}


def right_child(members):
    if len(members) == 0: return {}

    if len(members) > 1:
        child_member = getattr(find_right(*members), 'child_id')
    elif is_right(members[0]):
        child_member = getattr(members[0], 'child_id')
    else:
        child_member = None
    print child_member
    return load_users(child_member) if child_member else {}


def load_users(user):
    profile = Profile.objects.get(user=user)
    user_details = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_auto_id": profile.user_auto_id,
        "sponsor_id": profile.sponser_id.id,
        "placement_id": profile.placement_id.id,
        "mobile": profile.mobile,
        "placement_position": profile.placement_position
    }
    members = Members.objects.filter(parent_id=user.id)
    print "members is {}".format(members)
    if len(members) > 0:
        return {
            'left' : left_child(members),
            'right' : right_child(members),
            'user': user_details
        }
    else:
        return {
            'user':user_details,
            'left': {},
            'right': {}
        }