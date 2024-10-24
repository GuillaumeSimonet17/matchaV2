from flask import flash, Blueprint, render_template, session, redirect, url_for, request, abort


def update_user_infos(request):
    # call update
    if True:
        flash('C\'est carré : update infos', 'success')
    else:
        flash('Nan gros, t\'as pas compris...', 'danger')
    return render_template('user.html')

def change_password(request):
    # call update
    if True:
        flash('C\'est carré : update password', 'success')
    else:
        flash('Nan gros, t\'as pas compris...', 'danger')
    return redirect(url_for('main.user'))
