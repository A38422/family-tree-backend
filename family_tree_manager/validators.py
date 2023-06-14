from django.core.validators import RegexValidator


phone_regex = RegexValidator(
    regex=r'^\+?0\d{9,10}$',
    message="Số điện thoại không hợp lệ"
)
