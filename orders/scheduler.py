# orders/scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings

logger = logging.getLogger(__name__)

# 스케줄러 인스턴스
scheduler = None


def start_scheduler():
    """
    백그라운드 스케줄러를 시작합니다.
    Django 앱 시작 시 자동으로 호출됩니다.
    """
    global scheduler
    
    if scheduler is not None:
        print("⚠️  스케줄러가 이미 실행 중입니다.")
        return
    
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    
    # 30분마다 주문 수집 작업 실행
    scheduler.add_job(
        collect_orders_job,
        trigger=IntervalTrigger(minutes=30),
        id='collect_orders_30min',
        name='쇼핑몰 주문 자동 수집 (30분)',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ 주문 수집 스케줄러 시작: 30분마다 실행")


def stop_scheduler():
    """스케줄러를 중지합니다."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        print("⏹️  주문 수집 스케줄러 중지")


def collect_orders_job():
    """
    스케줄러에서 호출되는 주문 수집 작업
    """
    from orders.services import OrderCollectorService
    
    print("=== 주문 자동 수집 시작 ===")
    
    try:
        result = OrderCollectorService.collect_all_active_orders()
        print(f"✅ 주문 수집 완료: {result.get('message')}")
    except Exception as e:
        print(f"❌ 주문 수집 오류: {str(e)}")
        logger.error(f"주문 수집 오류: {str(e)}", exc_info=True)
