from django.contrib.auth.models import User
from addons.accounts.models import Profile, Members


def lower_encode(member, leg_list):
    val = str.lower(member.child_id.profile.placement_position.encode("utf-8"))
    return val in leg_list


def find_left(member1, member2):
    # member.child_id.profile will give profile object
    return member1 if lower_encode(member1, ('l', 'left')) else member2


def find_right(member1, member2):
    return member1 if lower_encode(member1, ('r', 'right')) else member2


def is_left(member):
    return lower_encode(member, ('l', 'left'))


def is_right(member):
    lower_encode(member, ('r', 'right'))


def new_user_text(ref_code, ref_kw):
    return {
        "text": {
            "name": "Add New User"
        },
        "link": {
            "href": ref_code + ref_kw
        }
    }

def get_field(model, attr, kw):
    # get_field(Profile, 'sponsor_id', 'id')
    if getattr(model, attr):
        return getattr(getattr(model, attr), kw)
    return None


def left_child(members, ref_code):
    if len(members) == 0: return {}

    if len(members) > 1:
        child_member = getattr(find_left(*members), 'child_id')
    elif is_left(members[0]):
        child_member = getattr(members[0], 'child_id')
    else:
        child_member = None
    return load_users(child_member, ref_code) if child_member else new_user_text(ref_code, "&pos=left")


def right_child(members, ref_code):
    if len(members) == 0: return {}

    if len(members) > 1:
        child_member = getattr(find_right(*members), 'child_id')
    elif is_right(members[0]):
        child_member = getattr(members[0], 'child_id')
    else:
        child_member = None
    return load_users(child_member, ref_code) if child_member else new_user_text(ref_code, "&pos=right")


def load_users(user, ref_code):
    ref_code = ref_code or ""
    profile = Profile.objects.get(user=user)
    # import pdb; pdb.set_trace()
    user_details = {
                "name": user.first_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "sponsor_id":  None if profile.sponser_id is None else profile.sponser_id.id,
                "placement_id": None if profile.placement_id is None else profile.placement_id.id,
                "mobile": profile.mobile,
                "placement_position": profile.placement_position
            }
    members = Members.objects.filter(parent_id=user.id)
    if len(members) > 0:
        return {
            "text": user_details,
            "image": "/static/images/node2.png",
            "link": {
                "href": profile.href
            },
            "children": [
                left_child(members, ref_code),
                right_child(members, ref_code)
            ]
        }
    else:
        return {
            "text": user_details,
            "image": "/static/images/node2.png",
            "link": {
                "href": profile.href
            },
            "children": [
                new_user_text(ref_code, "&pos=left"),
                new_user_text(ref_code, "&pos=right")
            ]
        }