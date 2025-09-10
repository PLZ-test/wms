# core/context_processors.py
from management.models import Center, Shipper # management 앱의 모델을 가져옴

def filters(request):
    selected_center_name = request.session.get('selected_center', '')

    shippers = Shipper.objects.all()
    if selected_center_name:
        shippers = shippers.filter(center__name=selected_center_name)

    return {
        'centers': Center.objects.all(),
        'shippers': shippers,
        'selected_center': selected_center_name,
        'selected_shipper': request.session.get('selected_shipper', ''),
    }