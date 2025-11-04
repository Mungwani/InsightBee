# apps/dataflow/common/models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date,
    Boolean, BigInteger, ForeignKey # DB 컬럼 타입을 정의하는 도구들
)
from sqlalchemy.orm import relationship # 테이블 간의 관계(Join)를 정의하는 도구
from sqlalchemy.ext.declarative import declarative_base # ORM 모델의 기반이 되는 클래스

# --- [SQLAlchemy 설정] ---
# SQLAlchemy의 Base 클래스 생성
# 여기에 정의된 모든 클래스들은 'Base'를 상속받아 DB 테이블로 매핑됨
Base = declarative_base()

# --- [테이블 1: 회사 정보] ---
class Companies(Base):
    """
    [회사 테이블 (companies)]
    DB의 'companies' 테이블 스키마를 정의합니다.
    [!!핵심 수정!!] 실제 DB 스키마에 맞춰 Primary Key를 'id'로 수정했습니다.
    """
    # __tablename__ : 실제 DB에 매핑될 테이블 이름
    __tablename__ = 'companies'

    # --- [컬럼 정의] ---
    # [!!핵심 수정!!] Primary Key (기본 키) 컬럼 이름을 'id'로 변경
    # id (PK, 정수)
    id = Column(Integer, primary_key=True) 

    # name_ko (문자열, 100자, 필수)
    name_ko = Column(String(100), nullable=False) 
    # name_en (문자열, 100자, 선택)
    name_en = Column(String(100))
    # corp_code (문자열, 50자, 고유값)
    corp_code = Column(String(50), unique=True) 
    # stock_code (문자열, 20자, 선택)
    stock_code = Column(String(20))
    # created_at (날짜/시간, 선택)
    created_at = Column(DateTime) 

    # --- [관계 정의] ---
    # 'NewsArticle' 클래스와의 관계 정의
    # 'company.news_articles' 형태로 이 회사에 속한 기사 목록을 참조할 수 있게 됨
    # (실제 관계 설정은 NewsArticle 클래스에서 'company'와 'news_articles'를
    #  상호 참조(back_populates)하도록 아래에서 정의됩니다.)
    

# --- [테이블 2: 수집된 뉴스 기사] ---
class NewsArticle(Base):
    """
    DB의 'news_articles' 테이블 스키마를 정의합니다.
    """
    __tablename__ = 'news_articles'

    # --- [컬럼 정의] ---
    
    # article_id (PK, 큰 정수, 자동 증가)
    article_id = Column(BigInteger, primary_key=True, autoincrement=True)

    # --- 1. 기본 기사 정보 및 관계 설정 ---
    
    #  company_id (FK, 정수, 필수, 인덱스)
    # 'companies' 테이블의 'id' 컬럼을 참조하는 외래 키(ForeignKey)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)

    # --- [관계 정의 (ORM 전용)] ---
    # (DB 스키마에 컬럼으로 생성되지 않음)
    
    # 1. 'company' 관계: NewsArticle 객체에서 'article.company'로 Companies 정보에 접근
    #    e.g., article.company.name_ko -> '삼성전자'
    #    back_populates="news_articles": Companies 모델의 'news_articles' 속성과 연결
    company = relationship("Companies", back_populates="news_articles")

    # 2. (역참조) Companies 클래스에 'news_articles' 속성을 동적으로 추가
    #    e.g., company.news_articles -> [<NewsArticle 1>, <NewsArticle 2>, ...]
    #    back_populates="company": NewsArticle 모델의 'company' 속성과 연결
    Companies.news_articles = relationship("NewsArticle", back_populates="company")

    # --- 2. 스크래핑된 기사 원문 정보 ---
    
    # title (문자열, 500자, 필수)
    title = Column(String(500), nullable=False)
    # url (문자열, 1000자, 필수, 고유값) - 원본 URL
    url = Column(String(1000), nullable=False, unique=True)
    # url_hash (문자열, 32자, 필수, 고유값, 인덱스) - URL의 MD5 해시 (중복 체크용)
    url_hash = Column(String(32), nullable=False, unique=True, index=True)
    # content (텍스트, 용량 무제한, 선택) - 스크래핑된 본문
    content = Column(Text, nullable=True)
    # published_at (날짜/시간, 선택) - 기사 발행일
    published_at = Column(DateTime, nullable=True)

    # --- 3. 필터링 및 메타 정보 ---
    
    # search_keyword (문자열, 100자, 선택) - Naver API 검색 시 사용한 키워드 (e.g., 'KT')
    search_keyword = Column(String(100), nullable=True)
    # score (정수, 필수, 기본값 0) - filter.py에서 계산된 점수
    score = Column(Integer, nullable=False, default=0)
    # matched_keywords (텍스트, 선택) - 점수 계산 시 매칭된 키워드 목록 (e.g., "[('채용', 15)]")
    matched_keywords = Column(Text, nullable=True)
    # is_passed_rule (불리언, 필수, 인덱스) - filter.py가 판단한 최종 통과 여부 (True/False)
    is_passed_rule = Column(Boolean, nullable=False, index=True)

    def __repr__(self):
        """
        [디버깅용]
        print(article_object) 실행 시 출력될 문자열을 정의합니다.
        로그나 터미널에서 객체를 쉽게 식별할 수 있게 도와줍니다.
        """
        status = "PASSED" if self.is_passed_rule else "FAILED"
        return f"<News(id={self.article_id}, status={status}, score={self.score}, title='{self.title[:20]}...')>"
