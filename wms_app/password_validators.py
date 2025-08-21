# wms_app/password_validators.py

# Django의 기본 비밀번호 검사기들을 가져옵니다. 이를 상속받아 메시지만 변경할 것입니다.
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomMinimumLengthValidator(MinimumLengthValidator):
    """
    기존 MinimumLengthValidator를 상속받아 오류 메시지만 한글로 변경합니다.
    """
    def validate(self, password, user=None):
        # 만약 비밀번호 길이가 최소 길이보다 짧으면, 우리가 지정한 메시지로 오류를 발생시킵니다.
        if len(password) < self.min_length:
            raise ValidationError(
                _("비밀번호는 %(min_length)d자리 이상으로 입력해주세요."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        # 도움말 텍스트도 한글로 변경합니다.
        return _(
            "비밀번호는 %(min_length)d자리 이상이어야 합니다."
        ) % {'min_length': self.min_length}


class CustomCommonPasswordValidator(CommonPasswordValidator):
    """
    기존 CommonPasswordValidator를 상속받아 오류 메시지만 한글로 변경합니다.
    """
    # 기본 오류 메시지를 우리가 원하는 한글 메시지로 덮어씁니다.
    DEFAULT_MESSAGE = _("타인이 예상할 수 없는 비밀번호를 사용해주세요.")

    def validate(self, password, user=None):
        # password가 흔한 비밀번호 목록에 있으면, 우리가 지정한 메시지로 오류를 발생시킵니다.
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                self.DEFAULT_MESSAGE,
                code='password_too_common',
            )


class CustomNumericPasswordValidator(NumericPasswordValidator):
    """
    기존 NumericPasswordValidator를 상속받아 오류 메시지만 한글로 변경합니다.
    """
    def validate(self, password, user=None):
        # password가 숫자로만 이루어져 있으면, 우리가 지정한 메시지로 오류를 발생시킵니다.
        if password.isdigit():
            raise ValidationError(
                _("비밀번호가 숫자로만 되어있어 안전하지 않습니다."),
                code='password_entirely_numeric',
            )