import os
import sys
import socket
import threading
import time

def get_ip_address():
    try:
        # 구글 DNS 서버에 연결하여 내 IP 확인 (실제 연결은 안 함)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_django():
    # 0.0.0.0으로 실행하여 외부 접속 허용
    os.system(f"{sys.executable} manage.py runserver 0.0.0.0:8000")

if __name__ == "__main__":
    ip = get_ip_address()
    hostname = socket.gethostname()
    
    print("\n" + "="*60)
    print("📢 WMS 서버를 시작합니다 (WiFi 접속 모드)")
    print("="*60)
    print(f"\n[접속 주소 안내]")
    print(f"1. 컴퓨터(PC)에서 접속할 때:")
    print(f"   👉 http://localhost:8000")
    print(f"\n2. 핸드폰(같은 와이파이)에서 접속할 때:")
    print(f"   👉 http://{ip}:8000")
    print(f"   (또는 http://{hostname}:8000 시도)")
    
    print(f"\n[참고] 와이파이 IP({ip})는 바뀔 수 있지만,")
    print(f"       이 파일을 실행하면 항상 현재 IP를 알려드립니다.")
    print("\n" + "="*60 + "\n")

    # 서버 실행
    try:
        run_django()
    except KeyboardInterrupt:
        pass
