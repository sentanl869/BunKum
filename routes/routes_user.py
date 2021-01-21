from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
)
from flask_login import current_user, login_user, logout_user, login_required

from models.user import User
from models.role import Role, Permission
from models.comment import Comment
from models.helper import send_email, current_user_object
from models.forms import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    ChangeEmailForm,
    PasswordResetForm,
    PasswordResetViewForm,
    ChangeAvatarForm,
    EditProfileForm,
    EditProfileAdminForm,
)
from routes import admin_required


main = Blueprint('user', __name__, url_prefix='/user')


@main.route('/login', methods=['GET', 'POST'])
def login() -> bytes:
    form = LoginForm()
    if form.validate_on_submit():
        user = User.one(email=form.email.data.lower())
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            target_url: str = request.args.get('next')
            if target_url is None or not target_url.startswith('/'):
                target_url = url_for('blog.index')
            return redirect(target_url)
        flash('用户名或密码无效。')
    return render_template('login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register() -> bytes:
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.register(
            email=form.email.data.lower(),
            username=form.username.data,
            password=form.password.data
        )
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Email 地址验证',
            '/email/confirm',
            user=user,
            token=token
        )
        flash('一封确认邮件已经发送至您的邮箱。')
        return redirect(url_for('user.login'))
    return render_template('register.html', form=form)


@main.route('/confirm/<token>')
@login_required
def confirm(token: str) -> bytes:
    if current_user.confirmed:
        return redirect(url_for('blog.index'))
    if current_user.confirm(token):
        flash('您已经确认了您的电子邮件地址，非常感谢！')
    else:
        flash('确认链接无效或已过期。')
    return redirect(url_for('blog.index'))


@main.route('/confirm')
@login_required
def resend_confirmation() -> bytes:
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        'Email 地址验证',
        '/email/confirm',
        user=current_user,
        token=token
    )
    flash('一封新的确认邮件已经发送至您的邮箱。')
    return redirect(url_for('blog.index'))


@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password() -> bytes:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.save()
            flash('您的密码已经更新。')
            return redirect(url_for('blog.index'))
        else:
            flash('您输入的密码无效。')
    return render_template('change_password.html', form=form)


@main.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email() -> bytes:
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                'Email 地址验证',
                '/email/change_email',
                user=current_user,
                token=token
            )
            flash('一封确认邮件已经发送至您的新邮箱。')
            return redirect(url_for('blog.index'))
        else:
            flash('您输入的邮件地址或密码无效。')
    return render_template('change_email.html', form=form)


@main.route('/change_email/<token>')
@login_required
def verify_change_email_token(token: str) -> bytes:
    if current_user.change_email(token):
        flash('您的邮件地址已经更新。')
    else:
        flash('您的请求无效。')
    return redirect(url_for('blog.index'))


@main.route('/reset', methods=['GET', 'POST'])
def password_reset() -> bytes:
    if not current_user.is_anonymous:
        return redirect(url_for('blog.index'))
    form = PasswordResetViewForm()
    if form.validate_on_submit():
        user = User.one(email=form.email.data.lower())
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                '重置密码',
                '/email/reset_password',
                token=token
            )
            flash('一封确认邮件已经发送至您的邮箱。')
            return redirect(url_for('user.login'))
    return render_template('reset_password.html', form=form)


@main.route('/reset/<token>', methods=['GET', 'POST'])
def verify_password_reset_token(token: str) -> bytes:
    if not current_user.is_anonymous:
        return redirect(url_for('blog.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash('您的密码已重置成功，请重新登录。')
            return redirect(url_for('user.login'))
        else:
            return redirect(url_for('blog.index'))
    return render_template('reset_password.html', form=form)


@main.route('/profile/<username>')
@login_required
def profile(username: str):
    user = User.one(username=username)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (user.comments.count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = user.comments_page(
        page,
        current_app.config['COMMENTS_PER_PAGE'],
        Comment.created_time.desc()
    )
    comments = pagination.items
    return render_template(
        'profile.html',
        user=user,
        comments=comments,
        pagination=pagination,
        page=page,
        next=request.full_path
    )


@main.route('/change_avatar/<username>', methods=['GET', 'POST'])
@login_required
def change_avatar(username: str) -> bytes:
    if current_user.username != username \
            and not current_user.can(Permission.ADMIN):
        abort(403)
    user = User.one(username=username)
    if user is None:
        abort(404)
    form = ChangeAvatarForm()
    if form.validate_on_submit():
        avatar_file = form.avatar.data
        avatar_url = user.avatar_save(avatar_file)
        User.update(
            user,
            avatar_url=avatar_url
        )
        flash('用户头像已经更新。')
        return redirect(url_for('user.profile', username=user.username))
    return render_template('change_avatar.html', form=form)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile() -> bytes:
    form = EditProfileForm(user=current_user)
    if form.validate_on_submit():
        User.update(
            current_user_object(current_user.id),
            username=form.username.data,
        )
        flash('您的个人资料已经更新。')
        return redirect(url_for('user.profile', username=current_user.username))
    form.username.data = current_user.username
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(_id: int) -> bytes:
    user = User.one(id=_id)
    if user is None:
        abort(404)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        User.update(
            user,
            email=form.email.data,
            username=form.username.data,
            confirmed=form.confirmed.data,
            role=Role.get(form.role.data),
        )
        target_url: str = request.args.get('next')
        if target_url is None or not target_url.startswith('/'):
            target_url = url_for('user.profile', username=user.username)
        flash('该用户的信息已被更新。')
        return redirect(target_url)
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/logout')
@login_required
def logout() -> bytes:
    logout_user()
    flash('您已经成功登出。')
    return redirect(url_for('blog.index'))


@main.route('/unconfirmed')
def unconfirmed() -> bytes:
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('blog.index'))
    return render_template('unconfirmed.html')
