from django.contrib.auth.models import User
from addons.accounts.models import Profile, Members
from django.conf import settings
from urllib2 import urlparse


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
    return lower_encode(member, ('r', 'right'))


def new_user_text(ref_code, *ref_kw):
    return {
        "text": {
            "name": "Add New User"
        },
        "link": {
            "href": "{}&{}".format(ref_code, '&'.join(*ref_kw))
        }
    }


def get_field(model, attr, kw):
    # get_field(Profile, 'sponsor_id', 'id')
    if getattr(model, attr):
        return getattr(getattr(model, attr), kw)
    return None


def get_placement_id(parent):
    return "parent_placement_id=%s" %(parent.profile.user_auto_id)


def left_child(members, ref_code):
    if len(members) == 0:
        raise Exception("left child shouldn't be invoked if members = 0")

    if len(members) > 1:
        res = find_left(*members)
        child_member = res.child_id
    elif is_left(members[0]):
        res = members[0]
        child_member = res.child_id
    else:
        child_member = None
        parent = members[0].parent_id
    return load_users(child_member, ref_code) if child_member else new_user_text(ref_code, ("pos=left", get_placement_id(parent)))


def right_child(members, ref_code):
    if len(members) == 0:
        raise Exception("right child shouldn't be invoked if members = 0")

    if len(members) > 1:
        res = find_right(*members)
        child_member = res.child_id
    elif is_right(members[0]):
        res = members[0]
        child_member = res.child_id
    else:
        child_member = None
        parent = members[0].parent_id
    return load_users(child_member, ref_code) if child_member else new_user_text(ref_code, (
        "pos=right", get_placement_id(parent)))


def load_users(user, ref_code):
    icon = urlparse.urljoin(getattr(settings, "STATIC_URL", "/static"), "images/node2.png")
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
            "image": icon,
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
            "image": icon,
            "link": {
                "href": urlparse.urljoin("https://www.avicrypto.com", "/network") + "#"  # profile.href
            },
            "children": [
                new_user_text(ref_code, ("pos=left", "parent_placement_id=%s" %(profile.user_auto_id))),
                new_user_text(ref_code, ("pos=right", "parent_placement_id=%s" %(profile.user_auto_id)))
            ]
        }


def get_left(user):
    """Helper Function: Gets leftmost user of tree"""
    members = Members.objects.filter(parent_id=user.id)
    assert len(members) <= 2

    if len(members) == 0:
        return None
    if len(members) > 1:
        res = find_left(*members)
        child_member = res.child_id
    elif is_left(members[0]):
        child_member = members[0].child_id
    else:
        child_member = None
    return child_member


def get_right(user):
    """Helper Function: Gets rightmost user of tree"""
    members = Members.objects.filter(parent_id=user.id)
    assert len(members) <= 2

    if len(members) == 0:
        return None
    if len(members) > 1:
        res = find_right(*members)
        child_member = res.child_id
    elif is_right(members[0]):
        child_member = members[0].child_id
    else:
        child_member = None
    return child_member


def find_min(user):
    """Gets leftmost user of tree"""
    min_user = get_left(user)
    return min_user if min_user else user

def find_max(user):
    """Gets rightmost user of tree"""
    max_user = get_right(user)
    return max_user if max_user else user

def find_min_max(user):
    return (find_min(user), find_max(user))