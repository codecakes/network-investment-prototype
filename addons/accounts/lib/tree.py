from addons.accounts.models import Profile, Members, User
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from django.db.models import Count, Min, Sum, Avg
from django.conf import settings
from urllib2 import urlparse
from functools import wraps

icon = urlparse.urljoin(getattr(settings, "STATIC_URL", "/static"), "images/node2.png")


def lower_encode(member, leg_list):
    if type(member) == Members:
        val = str.lower(member.child_id.profile.placement_position.encode("utf-8"))
    elif type(member) == User and member.profile.placement_position:
        val = str.lower(member.profile.placement_position.encode("utf-8"))
    else:
        return None
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


def tot_txn_vol(user):
    """Helper function to calculate total aggregated amount"""
    # TODO: integrate a redis cache decorator
    return sum(map(lambda w: Transactions.objects.filter(sender_wallet=w.uuid, \
                                                         reciever_wallet=w.uuid).aggregate(Sum('amount')), \
                   Wallet.objects.filter(owner=user)))


def num_children(user):
    """returns total nodes under this user"""
    pass


def get_field(model, attr, kw):
    # get_field(Profile, 'sponsor_id', 'id')
    if getattr(model, attr):
        return getattr(getattr(model, attr), kw)
    return None


def get_placement_id(parent):
    return 'parent_placement_id={}'.format(parent.profile.user_auto_id)


def new_user_text(ref_code, *ref_kw):
    # type: (string, list) -> dict
    href = "{}&{}".format(ref_code, '&'.join(*ref_kw))
    parent = '1'
    children = '0'
    user_auto_id = urlparse.urlparse('&pos=right&parent_placement_id=AVI000000020').path.split('=')[-1]
    profile = Profile.objects.get(user_auto_id=user_auto_id)
    parent_user = profile.user
    sibling = '1'  #''1' if get_left(parent_user) else '1' if get_right(parent_user) else '0'
    relationship = parent+sibling+children
    return dict(
        name="<a href= {}>Add New User</a>".format(href),
        relationship=relationship
    )


def left_child(members, ref_code, level):
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
    return load_users(child_member, ref_code, level=level) if child_member else new_user_text(ref_code,
                                                                                 ("pos=left", get_placement_id(parent)))


def right_child(members, ref_code, level):
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
    return load_users(child_member, ref_code, level=level) if child_member else new_user_text(ref_code, (
        "pos=right", get_placement_id(parent)))


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
    return find_min(min_user) if get_left(min_user) else min_user if min_user else user


def find_max(user):
    """Gets rightmost user of tree"""
    max_user = get_right(user)
    return find_max(max_user) if get_right(max_user) else max_user if max_user else user


def find_min_max(user):
    return (find_min(user), find_max(user))


def get_parent(child_user):
    return child_user.profile.placement_id


def is_parent_of(parent, child_user):
    """Checks if a child node `child_user` has a parent node user `parent`"""
    if parent == child_user:
        return child_user
    found_node = get_parent(child_user)  # child_user.profile.placement_id
    return None if found_node is None else True if found_node == parent else get_parent(found_node)


def is_member_of(parent_user, child_user, leg='l'):
    """Checks if child_user is in the selected leg of the parent subtree"""
    node = get_left(parent_user) if leg in ('l', 'left') else get_right(parent_user) \
        if leg in ('r', 'right') else None
    if node:
        found_node = is_parent_of(node, child_user)
        if found_node is None:
            message = "No such node placed under this sponsor. Would you like to add yourself down their line?"
            placement_id = node.profile.user_auto_id
        elif get_left(found_node):
            message = "This placement is full. Would you like to add yourself down their line?"
            node = find_min(found_node)
            placement_id = node.profile.user_auto_id
        elif get_left(found_node) is None:
            message = "success"
            placement_id = found_node.profile.user_auto_id
    else:
        message = "Empty Leg. No such child node. Would you like to add yourself there?"
        placement_id = parent_user.profile.user_auto_id
    return {'node': node, 'message': message, placement_id: placement_id}


def get_relationship(user):
    if type(user) == Profile:
        user = Profile.objects.get(user_id=user)
    parent_user = get_parent(user)
    parent = '1' if parent_user else '0'
    sibling = '1'
    # if is_left(user):
    #     sibling = '1' if get_right(parent_user) else '0'
    # elif is_right(user):
    #     sibling = '1' if get_left(parent_user) else '0'
    # else:
    #     sibling = '0'
    children = '1' if len(Members.objects.filter(parent_id=user)) > 0 else '0'
    return parent + sibling + children


def get_user_json(user, profile):
    return dict(id=user.id,
                relationship=get_relationship(user),
                name="%s %s" % (user.first_name, user.last_name),
                content="Total Transactional Volume: %s" % (tot_txn_vol(user)),
                sponsor_id=None if profile.sponser_id is None else profile.sponser_id.id,
                placement_id=None if profile.placement_id is None else profile.placement_id.id,
                placement_position=profile.placement_position, image=icon,
                link=dict(
                    href=urlparse.urljoin("https://www.avicrypto.us", "/network") + "#"))


def load_next_subtree(func):
    """Decorator for Stateless expandable subtree given a user"""
    @wraps(func)
    def wrapped_f(user, ref_code, **kw):
        """
        continues load_users if level not reached else stops with invite users

        :type ref_code: str
        :type user: object
        """
        l = kw.__getitem__('level')
        profile = Profile.objects.get(user=user)
        # import pdb; pdb.set_trace()
        if l > 0:
            l -= 1
            return func(user, ref_code, level=l)
        return get_user_json(user, profile)

    return wrapped_f


@load_next_subtree
def load_users(user, ref_code, level=4):
    """Generates json tree of users"""
    ref_code = ref_code or ""
    profile = Profile.objects.get(user=user)
    # import pdb; pdb.set_trace()
    members = Members.objects.filter(parent_id=user.id)

    user_json = get_user_json(user, profile)

    if len(members) > 0:
        user_json.update(
            dict(children=[
                left_child(members, ref_code, level),
                right_child(members, ref_code, level)
            ])
        )
    else:
        user_json.update(
            dict(children=[
                new_user_text(ref_code, ("pos=left", "parent_placement_id=%s" % (profile.user_auto_id))),
                new_user_text(ref_code, ("pos=right", "parent_placement_id=%s" % (profile.user_auto_id)))
            ])
        )
    return user_json
