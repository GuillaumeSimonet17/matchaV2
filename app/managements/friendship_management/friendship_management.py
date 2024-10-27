
# Gestion des intéractions Friendship
# écoute des events pour friendship


# EMIT
# - send invitation : (on btn in profile)
# check if friendship exist (au cas ou) : get_friendship_by_user_ids
# create if not, with state 'invitation'

# - send uninvitation : (on btn in profile)
# check if friendship state is 'connected' : get_friendship_by_user_ids
# update friendship sate by 'uninvitation' ou delete friendship ? Voir le sujet
# appeler la fonction block ? Voir le sujet

# - send connection : (on btn in profile)
# check if friendship state is 'invitation' and receiver_id == user_id : select_where_and
# update friendship sate by 'connected' : update_friendship_by_user_ids


# -------------------------------------------------------

# ON
# - receive invitaion : db already updated
# add a notif

# - receive uninvitaion :
# add a notif

# - receive connection :
# add a notif


# -------------------------------------------------------
