from wms_app.models import Center # Center 모델을 가져오기 위해 추가

class FilterPersistenceMiddleware:
    """
    HTTP 요청/응답 과정에서 필터 값을 세션에 저장하여 유지하는 미들웨어.
    사용자가 센터 필터를 변경하면, 화주사 필터를 초기화합니다.
    또한, 세션에 저장된 센터가 DB에 존재하지 않으면 세션 값을 초기화합니다.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # --- 아래 로직이 추가/수정 되었습니다 ---
        # 세션에서 현재 필터 값을 가져옴
        selected_center = request.session.get('selected_center')
        
        # 세션에 값이 있는데, 실제 DB에는 없는 경우 (삭제된 경우)
        if selected_center and not Center.objects.filter(name=selected_center).exists():
            # 세션 값을 초기화
            request.session['selected_center'] = ''
            request.session['selected_shipper'] = ''

        # GET 파라미터에 center_filter가 있으면 세션에 저장 (기존 로직)
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