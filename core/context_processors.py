# core/context_processors.py
from django.core.cache import cache  # Django 캐시 기능을 사용하기 위해 import
from management.models import Center, Shipper

def filters(request):
    """
    모든 템플릿에서 공통적으로 사용할 상단 필터(센터, 화주사) 데이터를 제공합니다.
    성능 향상을 위해 조회 결과를 캐시에 10분간 저장하여 사용합니다.
    """
    selected_center_name = request.session.get('selected_center', '')

    # 1. 'centers' 목록을 캐시에서 먼저 찾아봅니다.
    centers = cache.get('all_centers')
    if not centers:
        # 캐시에 없으면 DB에서 조회한 후, 'all_centers'라는 키로 600초(10분)간 캐시에 저장합니다.
        centers = Center.objects.all()
        cache.set('all_centers', centers, 600)

    # 2. 'shippers' 목록도 캐시에서 먼저 찾아봅니다.
    # 사용자가 센터를 선택했는지 여부에 따라 캐시 키를 다르게 설정합니다.
    cache_key = f"shippers_for_{selected_center_name or 'all'}"
    shippers = cache.get(cache_key)
    
    if not shippers:
        # 캐시에 없으면 DB에서 조회합니다.
        shippers = Shipper.objects.all()
        if selected_center_name:
            shippers = shippers.filter(center__name=selected_center_name)
        # 조회 결과를 600초(10분)간 캐시에 저장합니다.
        cache.set(cache_key, shippers, 600)

    # 템플릿에 전달할 context 데이터
    return {
        'centers': centers,
        'shippers': shippers,
        'selected_center': selected_center_name,
        'selected_shipper': request.session.get('selected_shipper', ''),
    }