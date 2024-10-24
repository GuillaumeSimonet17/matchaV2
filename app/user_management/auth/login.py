from flask import Blueprint, render_template, session, redirect, url_for, request, abort


def auth_login(request):
    username = request.form['username']
    password = request.form['password']
    
    if username == 'admin' and password == 'psd':  # Remplacez par votre logique
        session['username'] = username
        return True
    
    return False
