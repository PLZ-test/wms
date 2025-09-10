# core/middleware.py
from management.models import Center # management 앱의 모델을 가져옴

class FilterPersistenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        selected_center = request.session.get('selected_center')

        if selected_center and not Center.objects.filter(name=selected_center).exists():
            request.session['selected_center'] = ''
            request.session['selected_shipper'] = ''

        if 'center_filter' in request.GET:
            newly_selected_center = request.GET.get('center_filter')

            if request.session.get('selected_center') != newly_selected_center:
                request.session['selected_shipper'] = ''

            request.session['selected_center'] = newly_selected_center

        if 'shipper_filter' in request.GET:
            request.session['selected_shipper'] = request.GET.get('shipper_filter')

        response = self.get_response(request)
        return response