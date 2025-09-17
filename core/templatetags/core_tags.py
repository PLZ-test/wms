# core/templatetags/core_tags.py

from django import template

# [추가] Django 템플릿 라이브러리에 사용자 정의 태그/필터를 등록하기 위한 객체입니다.
register = template.Library()

@register.filter(name='get_attribute')
def get_attribute(obj, key):
    """
    # 템플릿에서 객체의 속성(attribute) 값을 동적으로 가져오는 필터입니다.
    # 예: {{ my_object|get_attribute:"name" }} -> my_object.name 과 동일하게 동작
    # generic_list.html 에서 테이블 컬럼을 동적으로 렌더링할 때 사용됩니다.
    """
    return getattr(obj, key, "")