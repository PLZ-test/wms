# orders/services/order_collector.py
import json
import logging
from datetime import datetime, timedelta
from django.db import transaction, models
from django.utils import timezone

from management.models import ShipperApiInfo, Shipper, SalesChannel, Product
from orders.models import Order, OrderItem, ApiCollectionLog
from orders.api_clients import (
    CoupangClient, NaverClient, ElevenSTClient,
    GmarketClient, AuctionClient, WemakepriceClient,
    TmonClient, InterparkClient
)

logger = logging.getLogger(__name__)


class OrderCollectorService:
    """
    쇼핑몰 API로부터 주문을 수집하는 서비스
    """
    
    # 쇼핑몰 타입과 API 클라이언트 매핑
    CLIENT_MAP = {
        'COUPANG': CoupangClient,
        'NAVER': NaverClient,
        '11ST': ElevenSTClient,
        'GMARKET': GmarketClient,
        'AUCTION': AuctionClient,
        'WEMAKEPRICE': WemakepriceClient,
        'TMON': TmonClient,
        'INTERPARK': InterparkClient,
    }
    
    @classmethod
    def collect_orders_for_shipper(cls, shipper_id: int, channel_type: str = None) -> dict:
        """
        특정 화주사의 주문을 수집합니다.
        
        Args:
            shipper_id: 화주사 ID
            channel_type: 특정 쇼핑몰만 수집 (None이면 모든 활성화된 쇼핑몰)
        
        Returns:
            수집 결과 딕셔너리
        """
        try:
            shipper = Shipper.objects.get(id=shipper_id)
        except Shipper.DoesNotExist:
            return {'status': 'error', 'message': '화주사를 찾을 수 없습니다.'}
        
        # API 정보 조회
        api_infos = ShipperApiInfo.objects.filter(
            shipper=shipper,
            is_active=True
        )
        
        if channel_type:
            api_infos = api_infos.filter(channel_type=channel_type)
        
        if not api_infos.exists():
            return {'status': 'error', 'message': '활성화된 API 정보가 없습니다.'}
        
        total_collected = 0
        total_success = 0
        total_error = 0
        total_duplicate = 0
        results = []
        
        for api_info in api_infos:
            result = cls._collect_from_channel(shipper, api_info)
            results.append(result)
            total_collected += result.get('collected_count', 0) # 신규 생성 (성공+오류)
            total_success += result.get('success_count', 0)
            total_error += result.get('error_count', 0)
            total_duplicate += result.get('duplicate_count', 0)
        
        # [수정] 심플하고 명확한 메시지 (전체 처리 기준)
        total_total = total_collected + total_duplicate
        message = f"총 {total_total}건 처리 (신규 성공: {total_success}, 신규 오류: {total_error}, 중복: {total_duplicate})"
        
        return {
            'status': 'success',
            'message': message,
            'results': results
        }
    
    @classmethod
    def collect_all_active_orders(cls) -> dict:
        """
        모든 활성화된 API에서 주문을 수집합니다. (스케줄러에서 호출)
        
        Returns:
            수집 결과 딕셔너리
        """
        api_infos = ShipperApiInfo.objects.filter(is_active=True).select_related('shipper')
        
        if not api_infos.exists():
            logger.info("활성화된 API 정보가 없습니다.")
            return {'status': 'info', 'message': '활성화된 API 정보가 없습니다.'}
        
        total_collected = 0
        total_success = 0
        total_error = 0
        total_duplicate = 0
        results = []
        
        for api_info in api_infos:
            try:
                result = cls._collect_from_channel(api_info.shipper, api_info)
                results.append(result)
                total_collected += result.get('collected_count', 0) # 신규 생성 (성공+오류)
                total_success += result.get('success_count', 0)
                total_error += result.get('error_count', 0)
                total_duplicate += result.get('duplicate_count', 0)
            except Exception as e:
                logger.error(f"주문 수집 오류 ({api_info}): {str(e)}")
                results.append({
                    'shipper': api_info.shipper.name,
                    'channel': api_info.get_channel_type_display(),
                    'status': 'error',
                    'message': str(e)
                })
        
        # [수정] 심플하고 명확한 메시지 (전체 처리 기준)
        total_total = total_collected + total_duplicate
        message = f"총 {total_total}건 처리 (신규 성공: {total_success}, 신규 오류: {total_error}, 중복: {total_duplicate})"
        
        logger.info(message)
        return {
            'status': 'success',
            'message': message,
            'results': results
        }
    
    @classmethod
    # [수정] transaction.atomic 제거: 개별 주문 저장 실패가 전체 롤백을 유발하지 않도록 함
    def _collect_from_channel(cls, shipper: Shipper, api_info: ShipperApiInfo) -> dict:
        """
        특정 쇼핑몰 채널에서 주문을 수집합니다.
        
        Args:
            shipper: 화주사 객체
            api_info: API 정보 객체
        
        Returns:
            수집 결과 딕셔너리
        """
        channel_type = api_info.channel_type
        channel_name = api_info.get_channel_type_display()
        
        # API 클라이언트 생성
        client_class = cls.CLIENT_MAP.get(channel_type)
        if not client_class:
            return {
                'shipper': shipper.name,
                'channel': channel_name,
                'status': 'error',
                'message': f'지원하지 않는 쇼핑몰입니다: {channel_type}'
            }
        
        try:
            extra_info = json.loads(api_info.extra_info) if api_info.extra_info else {}
        except json.JSONDecodeError:
            extra_info = {}
        
        client = client_class(
            access_key=api_info.access_key,
            secret_key=api_info.secret_key,
            extra_info=extra_info
        )
        
        # 최근 30분 주문 조회
        end_date = timezone.now()
        start_date = end_date - timedelta(minutes=30)
        
        try:
            # API에서 주문 조회
            orders_data = client.fetch_orders(start_date, end_date)
            
            success_count = 0
            error_count = 0
            duplicate_count = 0  # [추가] 중복 건수 카운트
            error_messages = []
            
            # 판매 채널 객체 가져오기 또는 생성
            sales_channel, _ = SalesChannel.objects.get_or_create(name=channel_name)
            
            for order_data in orders_data:
                try:
                    # 중복 체크 - 같은 order_no가 있는지 확인
                    existing_order = Order.objects.filter(order_no=order_data.get('order_no')).first()
                    if existing_order:
                        duplicate_count += 1  # [추가] 중복 카운트 증가
                        print(f"⚠️  중복 주문번호 발견, 건너뜀: {order_data.get('order_no')}")
                        continue
                    
                    # 주문 생성
                    order = Order.objects.create(
                        shipper=shipper,
                        channel=sales_channel,
                        order_no=order_data.get('order_no'),
                        # [수정] 수집된 주문을 리스트 상단(오늘)에 무조건 노출시키기 위해 현재 시간 사용
                        # 원본 주문일자는 필요하다면 별도 필드나 비고에 저장 고려
                        order_date=timezone.now(),
                        recipient_name=order_data.get('recipient_name', ''),
                        recipient_phone=order_data.get('recipient_phone', ''),
                        address=order_data.get('address', ''),
                        postcode=order_data.get('postcode', ''),
                        delivery_memo=order_data.get('delivery_memo', ''),
                        order_status='PENDING'
                    )
                    
                    print(f"✅ Order 생성 성공: ID={order.id}, 주문번호={order.order_no}, 날짜={order.order_date.strftime('%Y-%m-%d')}")
                    
                    # [수정] 주문 단위로 성공/실패 판단하기 위한 플래그
                    order_has_error = False
                    
                    # 주문 상품 생성
                    for item_data in order_data.get('items', []):
                        product_identifier = item_data.get('product_identifier')
                        quantity = item_data.get('quantity', 1)
                        
                        # 상품 조회 (바코드 또는 이름으로)
                        try:
                            product = Product.objects.filter(
                                shipper=shipper
                            ).filter(
                                models.Q(barcode=product_identifier) |
                                models.Q(name=product_identifier)
                            ).first()
                            
                            if product:
                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    quantity=quantity
                                )
                                print(f"✅ OrderItem 생성 성공: 상품 {product.name}")
                            else:
                                # 상품을 찾을 수 없으면 오류로 처리
                                # JSON 직렬화를 위해 datetime을 문자열로 변환
                                serializable_data = order_data.copy()
                                if 'order_date' in serializable_data and isinstance(serializable_data['order_date'], datetime):
                                    serializable_data['order_date'] = serializable_data['order_date'].isoformat()
                                
                                order.order_status = 'ERROR'
                                order.error_message = json.dumps({
                                    'error_message': f'미등록 상품: {product_identifier}',
                                    'error_fields': ['product_identifier'],
                                    'original_data': serializable_data
                                }, ensure_ascii=False)
                                order.save()
                                order_has_error = True  # [수정] 플래그 설정
                                error_messages.append(f'미등록 상품: {product_identifier}')
                                print(f"⚠️  상품 없음, ERROR로 변경: {product_identifier}")
                                break  # [추가] 오류 발생 시 더 이상 상품 처리하지 않음
                        except Exception as e:
                            order_has_error = True  # [수정] 플래그 설정
                            error_messages.append(f'상품 처리 오류: {str(e)}')
                            print(f"❌ 상품 처리 오류: {str(e)}")
                            break  # [추가] 오류 발생 시 더 이상 상품 처리하지 않음
                    
                    # [추가] 주문 단위로 성공/오류 카운트
                    if order_has_error:
                        error_count += 1
                    else:
                        success_count += 1
                            
                except Exception as e:
                    # [수정] 주문 생성 중 에러 발생 시에도 DB에 'ERROR' 상태로 저장하여 누락 방지
                    error_count += 1
                    err_msg = str(e)
                    error_messages.append(f'주문 생성 오류: {err_msg}')
                    logger.error(f"주문 생성 실패 ({channel_name}): {err_msg}")
                    print(f"❌ 주문 생성 실패: {err_msg}")
                    
                    try:
                        # 최소한의 정보로 오류 주문 생성 시도
                        # JSON 직렬화를 위해 datetime 처리
                        serializable_data = order_data.copy()
                        if 'order_date' in serializable_data and isinstance(serializable_data['order_date'], datetime):
                            serializable_data['order_date'] = serializable_data['order_date'].isoformat()
                            
                        Order.objects.create(
                            shipper=shipper,
                            channel=sales_channel, # 위에서 생성/조회한 channel 재사용
                            order_no=order_data.get('order_no'),
                            order_date=order_data.get('order_date', timezone.now()),
                            recipient_name=order_data.get('recipient_name', '알수없음'),
                            recipient_phone=order_data.get('recipient_phone', ''),
                            address=order_data.get('address', ''),
                            order_status='ERROR',
                            error_message=json.dumps({
                                'error_message': f'시스템 오류: {err_msg}',
                                'error_fields': [],
                                'original_data': serializable_data
                            }, ensure_ascii=False)
                        )
                    except Exception as create_err:
                        # 오류 주문 저장조차 실패하면 어쩔 수 없이 로그만 남김 (매우 드문 케이스)
                        logger.critical(f"오류 주문 저장 실패: {str(create_err)}")
            
            # 수집 로그 기록
            log_status = 'SUCCESS' if error_count == 0 else ('PARTIAL' if success_count > 0 else 'FAILED')
            ApiCollectionLog.objects.create(
                shipper=shipper,
                channel_type=channel_type,
                status=log_status,
                total_count=len(orders_data),
                success_count=success_count,
                error_count=error_count,
                error_message='; '.join(error_messages[:5]) if error_messages else ''  # 처음 5개만
            )
            
            # [수정] 실제 생성된 주문 수 반환 (중복 제외)
            actual_created_count = success_count + error_count
            
            return {
                'shipper': shipper.name,
                'channel': channel_name,
                'status': 'success',
                'collected_count': actual_created_count,  # [수정] 실제 생성된 주문 수
                'success_count': success_count,
                'error_count': error_count,
                'duplicate_count': duplicate_count,  # [추가] 중복 건수
                'api_total_count': len(orders_data)  # [추가] API에서 받아온 전체 건수
            }
            
        except Exception as e:
            logger.error(f"API 호출 실패 ({channel_name}): {str(e)}")
            
            # 실패 로그 기록
            ApiCollectionLog.objects.create(
                shipper=shipper,
                channel_type=channel_type,
                status='FAILED',
                total_count=0,
                success_count=0,
                error_count=0,
                error_message=str(e)
            )
            
            return {
                'shipper': shipper.name,
                'channel': channel_name,
                'status': 'error',
                'message': str(e)
            }
