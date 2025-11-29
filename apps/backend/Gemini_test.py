import os
import warnings
from typing import List, Dict, Tuple

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from tqdm.auto import tqdm as auto_tqdm # pandas.apply 진행률 표시를 위함

# --- 1. 설정 (Configuration) ---
INPUT_FILENAME = "news_test.csv"
OUTPUT_FILENAME = "news_classified_results_representatives2.csv"
EMBEDDING_MODEL_NAME = 'distiluse-base-multilingual-cased-v1'
GEMINI_MODEL_NAME = 'gemini-2.5-flash' # 또는 'gemini-1.0-pro' 등 사용 가능한 모델
TOPIC_CATEGORIES = [
    "신사업/M&A", "경영전략/리더십", "해외진출/글로벌 동향", "투자유치/재무", "신제품/서비스 출시",
    "기술개발/R&D", "생산/공급망 관리", "특허/기술인증", "시장동향/트렌드 분석", "경쟁사 동향",
    "정부규제/정책", "인재채용/인재상", "조직문화/인사제도", "임직원 동정/인사", "노사관계/고용이슈",
    "ESG/지속가능경영", "사회공헌/CSR", "소비자보호/분쟁", "파트너십/협력", "대외활동/홍보", "리스크/위기관리"
]

def setup_gemini() -> genai.GenerativeModel:
    """API 키를 설정하고 Gemini 모델을 초기화합니다."""
    load_dotenv()
    warnings.filterwarnings("ignore")
    auto_tqdm.pandas(desc="개별 기사 분석(요약+분류) 중") # tqdm.pandas() 활성화
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("'.env' 파일에서 GOOGLE_API_KEY를 찾을 수 없습니다.")
        genai.configure(api_key=api_key)
        print("✅ Gemini API 키가 성공적으로 설정되었습니다.")
        return genai.GenerativeModel(GEMINI_MODEL_NAME)
    except Exception as e:
        print(f"❌ API 키 또는 모델 설정 중 오류 발생: {e}")
        exit()

def load_and_preprocess_data(filepath: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 분석에 맞게 전처리합니다."""
    print(f"\n1단계: '{filepath}' 파일 로딩 및 전처리...")
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
    except FileNotFoundError:
        print(f"❌ 오류: '{filepath}' 파일을 찾을 수 없습니다.")
        exit()

    df.columns = df.columns.str.strip()
    if '본문' in df.columns: df.rename(columns={'본문': 'content'}, inplace=True)
    if '제목' in df.columns: df.rename(columns={'제목': 'title'}, inplace=True)
    df.dropna(subset=['title', 'content'], inplace=True)
    df.drop_duplicates(subset=['title'], keep='first', inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"✅ 총 {len(df)}개의 고유한 뉴스 기사를 준비했습니다.")
    return df

def cluster_articles(df: pd.DataFrame) -> pd.DataFrame:
    """SentenceTransformer를 사용하여 '거의 동일한' 기사들을 그룹화합니다."""
    print(f"\n2단계: '{EMBEDDING_MODEL_NAME}' 모델로 중복 기사 그룹화...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    embeddings = model.encode(df['content'].tolist(), show_progress_bar=True)
    
    # [핵심] '거의 동일한 이벤트'를 묶도록 기준을 상향 (threshold=0.8)
    clusters = util.community_detection(embeddings, min_community_size=2, threshold=0.8)
    
    doc_id_to_cluster_id = {doc_id: i for i, cluster in enumerate(clusters) for doc_id in cluster}
    
    df['cluster_id'] = df.index.map(lambda x: doc_id_to_cluster_id.get(x, -1))
    print(f"✅ {len(clusters)}개의 고유한 이벤트(중복 그룹)를 발견했습니다.")
    return df

# [신규] 3단계: 개별 기사 분석 (요약 + 분류)
def get_summary_and_topic(content: str, model: genai.GenerativeModel, categories: List[str]) -> Tuple[str, str]:
    """
    단일 기사 본문을 받아, [요약]과 [토픽]을 한 번의 API 호출로 반환합니다.
    """
    category_list_str = f"[{', '.join(categories)}]"
    
    # [프롬프트 고도화] 요약과 분류를 한 번에 요청
    prompt = (
        f"당신은 취업 준비생의 면접 준비를 돕는 전문 커리어 애널리스트입니다.\n"
        f"다음 뉴스 기사 본문을 읽고, 2가지 임무를 수행해주세요.\n\n"
        f"1. **[의미 요약]**: 이 뉴스가 지원자에게 어떤 의미가 있는지(성장 동력, 위기, 인재상 등)에 초점을 맞춰 2-3문장으로 요약합니다.\n"
        f"2. **[토픽 분류]**: 주어진 '토픽 목록'에서 이 기사의 핵심 주제와 가장 적합한 카테리 하나만을 선택합니다.\n\n"
        f"--- 토픽 목록 ---\n{category_list_str}\n\n"
        f"--- 기사 본문 ---\n{content}\n\n"
        f"--- [중요] 응답 형식 ---\n"
        f"반드시 아래와 같은 형식으로만 응답해야 합니다. (다른 설명 없이):\n"
        f"요약: [여기에 1번 임무의 요약 내용을 작성]\n"
        f"토픽: [여기에 2번 임무의 토픽을 작성]"
    )
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # [응답 파싱] "요약:", "토픽:"을 기준으로 텍스트 분리
        summary_part = "요약 실패"
        topic_part = "분류 실패"
        
        if "요약:" in text and "토픽:" in text:
            summary_raw = text.split("요약:")[1].split("토픽:")[0].strip()
            topic_raw = text.split("토픽:")[1].strip()
            
            summary_part = summary_raw
            # 토픽 목록에 있는 유효한 카테고리인지 한번 더 확인
            topic_part = next((cat for cat in categories if cat in topic_raw), "분류 실패")
        else:
            # 예외: 형식을 지키지 않은 응답
            summary_part = text[:150] + "..." # 응답의 일부라도 저장
            
        return summary_part, topic_part
    
    except Exception as e:
        return f"요약 중 오류 발생: {e}", f"분류 중 오류 발생: {e}"


def main():
    """메인 실행 함수"""
    gemini_model = setup_gemini()
    df = load_and_preprocess_data(INPUT_FILENAME)
    df_clustered = cluster_articles(df)
    
    # --- 중복 기사 제거 및 대표 기사 선정 ---
    print("\n중간 단계: 각 그룹별 대표 기사 1개씩 선정...")
    df_representatives = df_clustered[df_clustered['cluster_id'] != -1].drop_duplicates(subset=['cluster_id'], keep='first')
    df_others = df_clustered[df_clustered['cluster_id'] == -1]
    df_filtered = pd.concat([df_representatives, df_others]).sort_index()
    
    print(f"✅ '기타'(고유) 기사 {len(df_others)}개와 '대표' 기사 {len(df_representatives)}개를 포함, 총 {len(df_filtered)}개로 압축되었습니다.")
    # --- 로직 끝 ---

    
    # --- [신규] 3단계: 압축된 리스트에 대해 개별 분석 (요약 + 분류) 실행 ---
    print(f"\n3단계: Gemini API로 {len(df_filtered)}개의 고유/대표 기사 분석 시작...")
    
    # .progress_apply()를 사용하여 진행률 표시줄과 함께 모든 행에 함수 적용
    # 이 함수는 (summary, topic) 튜플을 반환합니다.
    results = df_filtered['content'].progress_apply(
        lambda x: get_summary_and_topic(x, gemini_model, TOPIC_CATEGORIES)
    )

    # 튜플로 반환된 결과를 두 개의 새로운 열('summary', 'topic')로 분리
    df_final = df_filtered.copy()
    df_final['summary'] = results.apply(lambda x: x[0])
    df_final['topic'] = results.apply(lambda x: x[1])
    
    df_final.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
    
    print(f"\n🎉 모든 분석이 완료되었습니다! 결과가 '{OUTPUT_FILENAME}' 파일에 저장되었습니다.")
    print("\n--- 최종 토픽 분류 요약 ---")
    print(df_final['topic'].value_counts())

if __name__ == "__main__":
    main()