import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import warnings

def test_db_connection():
    """
    .env 파일의 DATABASE_URL을 읽어 Cloud SQL 연결을 테스트합니다.
    (psycopg3 드라이버 사용 기준)
    """
    
    print("Cloud SQL 연결 테스트를 시작합니다...")
    
    # 1. .env 파일 로드
    load_dotenv()
    warnings.filterwarnings("ignore", category=DeprecationWarning) 

    db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        print("❌ 오류: '.env' 파일에서 DATABASE_URL을 찾을 수 없습니다.")
        print("파일이 스크립트와 같은 위치에 있는지, 변수 이름이 정확한지 확인해주세요.")
        return

    print(f"로드된 DATABASE_URL: postgresql+psycopg://[사용자이름]:[비밀번호]@[IP주소]/[DB이름]")
    print("(보안을 위해 실제 값은 숨깁니다.)")

    try:
        # 2. 데이터베이스 엔진 생성
        engine = create_engine(db_url, connect_args={'connect_timeout': 10})

        # 3. 실제 연결 시도 및 간단한 쿼리 실행
        print("\n데이터베이스에 연결을 시도합니다... (최대 10초)")
        with engine.connect() as connection:
            # 'SELECT 1'은 DB가 살아있는지 확인하는 가장 간단한 쿼리입니다.
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("\n" + "="*40)
                print("🎉 축하합니다! Cloud SQL 연결에 성공했습니다.")
                print("="*40)
                print(".env 파일의 정보와 GCP IP 등록이 올바르게 완료되었습니다.")
            else:
                print("❌ 연결은 되었으나, 쿼리 실행에 실패했습니다.")

    # 오류 유형별로 더 상세한 진단 메시지 제공
    except OperationalError as e:
        error_message = str(e).lower()
        print("\n" + "!"*40)
        print("❌ 연결 실패: 데이터베이스 연결 중 [운영 오류]가 발생했습니다.")
        print("!"*40)
        
        if "getaddrinfo failed" in error_message or "could not translate host name" in error_message:
            print("\n[진단]: '호스트(IP 주소)를 찾을 수 없음' 오류입니다.")
            print("  ➡️ 원인: .env 파일의 `DATABASE_URL`에 있는 IP 주소 또는 형식이 잘못되었습니다.")
        elif "password authentication failed" in error_message:
            print("\n[진단]: '비밀번호 인증 실패' 오류입니다.")
            print("  ➡️ 원인: .env 파일의 [사용자이름] 또는 [비밀번호]가 틀렸습니다.")
        elif "connection refused" in error_message or "timeout" in error_message:
            print("\n[진단]: '연결 거부' 또는 '시간 초과' 오류입니다.")
            print("  ➡️ 원인: GCP 방화벽이 내 PC의 접속을 차단하고 있습니다. (현재 IP 주소 재등록 필요)")
        
        print("\n[오류 원인 상세 정보]:")
        print(e)

    except Exception as e:
        print("\n" + "!"*40)
        print(f"❌ 연결 실패: 예상치 못한 오류가 발생했습니다. (오류 유형: {type(e).__name__})")
        print("!"*40)
        print("\n[오류 원인 상세 정보]:")
        print(e)


if __name__ == "__main__":
    test_db_connection()