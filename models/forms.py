from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_pagedown.fields import PageDownField
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,Length, Email, Regexp, EqualTo, Optional
)
from wtforms import ValidationError

from models.user import User
from models.role import Role
from models.category import Category
from models.helper import get_size


class LoginForm(FlaskForm):
    email = StringField(
        '邮箱：',
        validators=[
            DataRequired(), Length(1, 64), Email()
        ]
    )
    password = PasswordField('密码：', validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField(
        '邮箱：',
        validators=[
            DataRequired(), Length(1, 64), Email()
        ]
    )
    username = StringField(
        '用户名：',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[\u4e00-\u9fa5\x00-\xffA-Za-z0-9][\u4e00-\u9fa5\x00-\xffA-Za-z0-9_.]*$',
                0,
                '用户名必须只包含汉字、字母、数字、点和下划线'
            )
        ]
    )
    password = PasswordField(
        '密码：',
        validators=[
            DataRequired(),
            EqualTo('password2', message='密码必须相同。')
        ]
    )
    password2 = PasswordField('确认密码：', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.one(email=field.data.lower()):
            raise ValidationError('该邮箱已经注册')

    def validate_username(self, field):
        if User.one(username=field.data):
            raise ValidationError('该用户名已被使用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('请输入旧密码：', validators=[DataRequired()])
    password = PasswordField(
        '请输入新密码：',
        validators=[
            DataRequired(),
            EqualTo(
                'password2',
                message='两次输入的密码必须一致'
            )
        ]
    )
    password2 = PasswordField('再次输入新密码：', validators=[DataRequired()])
    submit = SubmitField('更改密码')


class ChangeEmailForm(FlaskForm):
    email = StringField(
        '请输入新邮箱：',
        validators=[
            DataRequired(), Length(1, 64), Email()
        ]
    )
    password = PasswordField('请输入密码：', validators=[DataRequired()])
    submit = SubmitField('更改邮箱')

    def validate_email(self, field):
        if User.one(email=field.data.lower()):
            raise ValidationError('该邮箱已经注册')


class PasswordResetViewForm(FlaskForm):
    email = StringField(
        '邮箱：',
        validators=[
            DataRequired(), Length(1, 64), Email()
        ]
    )
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        '请输入新密码：',
        validators=[
            DataRequired(),
            EqualTo(
                'password2',
                message='两次输入的密码必须一致'
            )
        ]
    )
    password2 = PasswordField('再次输入新密码：', validators=[DataRequired()])
    submit = SubmitField('重置密码')


class ChangeAvatarForm(FlaskForm):
    avatar = FileField(
        '更改头像：',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png'], '仅支持 JPG、JPEG 和 PNG 格式')
        ]
    )
    submit = SubmitField('保存更改')

    def validate_avatar(self, field):
        if get_size(field.data) > (200 * 1024):
            raise ValidationError('图片大小超过 200KB 限制，请重新上传')


class EditProfileForm(FlaskForm):
    username = StringField(
        '更改用户名：',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[\u4e00-\u9fa5\x00-\xffA-Za-z0-9][\u4e00-\u9fa5\x00-\xffA-Za-z0-9_.]*$',
                0,
                '用户名必须只包含汉字、字母、数字、点和下划线'
            )
        ]
    )
    submit = SubmitField('保存更改')

    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username \
                and User.one(username=field.data):
            raise ValidationError('该用户名已被使用')


class EditProfileAdminForm(FlaskForm):
    email = StringField(
        '邮箱：',
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    username = StringField(
        '用户名：',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[\u4e00-\u9fa5\x00-\xffA-Za-z0-9][\u4e00-\u9fa5\x00-\xffA-Za-z0-9_.]*$',
                0,
                '用户名必须只包含汉字、字母、数字、点和下划线'
            )
        ]
    )
    confirmed = BooleanField('认证')
    role = SelectField('身份', coerce=int)
    submit = SubmitField('应用更改')

    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.role.choices = [
            (role.id, role.name) for role in Role.order(Role.name)
        ]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email \
                and User.one(email=field.data):
            raise ValidationError('该邮箱已经注册')

    def validate_username(self, field):
        if field.data != self.user.username \
                and User.one(username=field.data):
            raise ValidationError('该用户名已被使用')


class PostForm(FlaskForm):
    title = StringField('博客标题：', validators=[DataRequired(), Length(1, 64)])
    category = SelectField('文章分类：', coerce=int, default=1)
    new_category = StringField('新分类：', validators=[Optional(), Length(1, 64)])
    content = PageDownField(
        '此刻有什么想法？',
        validators=[DataRequired()],
        render_kw={'rows': 10}
    )
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name) for category in Category.order(Category.name)
        ]

    def validate_new_category(self, field):
        if Category.one(name=field.data):
            raise ValidationError('该分类标签已经存在')


class CommentForm(FlaskForm):
    content = TextAreaField(
        '',
        validators=[DataRequired()],
        render_kw={'rows': 4})
    submit = SubmitField('发表评论')


class EditCategoryForm(FlaskForm):
    name = StringField('名称：', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('应用更改')

    def __init__(self, category, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.category = category

    def validate_name(self, field):
        if field.data != self.category.name \
                and Category.one(name=field.data):
            raise ValidationError('该分类标签已经存在')


class EditCommentForm(FlaskForm):
    content = PageDownField(
        '',
        validators=[DataRequired()],
        render_kw={'rows': 10}
    )
    disabled = BooleanField('屏蔽')
    submit = SubmitField('应用更改')


class MessageForm(FlaskForm):
    content = PageDownField(
        '',
        validators=[DataRequired()],
        render_kw={'rows': 10}
    )
    submit = SubmitField('发送')


class EditMessageForm(FlaskForm):
    content = PageDownField(
        '',
        validators=[DataRequired()],
        render_kw={'rows': 10}
    )
    author_delete = BooleanField('发送方删除')
    receiver_delete = BooleanField('接收方删除')
    submit = SubmitField('应用更改')
