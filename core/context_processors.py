# core/context_processors.py
from management.models import Center, Shipper # management 앱의 모델을 가져와야 합니다.

def filters(request):
    """
    모든 템플릿에서 공통적으로 사용할 상단 필터(센터, 화주사) 데이터를 제공합니다.
    """
    selected_center_name = request.session.get('selected_center', '')
    
    # 전체 화주사를 기본으로 가져옵니다.
    shippers = Shipper.objects.all()
    
    # 만약 특정 센터가 선택되었다면, 해당 센터에 속한 화주사만 필터링합니다.
    if selected_center_name:
        shippers = shippers.filter(center__name=selected_center_name)

    # 템플릿에 전달할 context 데이터
    return {
        'centers': Center.objects.all(),
        'shippers': shippers,
        'selected_center': selected_center_name,
        'selected_shipper': request.session.get('selected_shipper', ''),
    }