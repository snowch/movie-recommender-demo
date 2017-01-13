from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import forms
from . import auth
from .. import app
from .forms import LoginForm, RegistrationForm
from .. import models


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.find_by_email(form.email.data)

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/change_password')
@login_required
def change_password():
    return render_template('/not_implemented_yet.html')


@auth.route('/reset_password')
def reset_password():
    return render_template('/not_implemented_yet.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = models.User(None, form.email.data, form.password.data)
        user.save()

        #token = user.generate_confirmation_token()
        # send_email(user.email, 'Confirm Your Account',
        #           'auth/email/confirm', user=user, token=token)
        #flash('A confirmation email has been sent to you by email.')

        flash('Your account has been created - please login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

