# core/middleware.py
from management.models import Center # management 앱의 모델을 가져옴

class FilterPersistenceMiddleware:
    """
    HTTP 요청/응답 과정에서 필터 값을 세션에 저장하여 유지하는 미들웨어.
    사용자가 센터 필터를 변경하면, 화주사 필터를 초기화합니다.
    또한, 세션에 저장된 센터가 DB에 존재하지 않으면 세션 값을 초기화합니다.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        selected_center = request.session.get('selected_center')

        if selected_center and not Center.objects.filter(name=selected_center).exists():
            request.session['selected_center'] = ''
            request.session['selected_shipper'] = ''

        if 'center_filter' in request.GET:
            newly_selected_center = request.GET.get('center_filter')
            
            # 선택된 센터가 변경되면 화주사 필터도 초기화
            if request.session.get('selected_center') != newly_selected_center:
                request.session['selected_shipper'] = ''

            request.session['selected_center'] = newly_selected_center

        # GET 파라미터에 shipper_filter가 있으면 세션에 저장
        if 'shipper_filter' in request.GET:
            request.session['selected_shipper'] = request.GET.get('shipper_filter')

        response = self.get_response(request)
        return response