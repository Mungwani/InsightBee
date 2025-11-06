import os
import warnings
from typing import List, Dict

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from tqdm.auto import tqdm as auto_tqdm # pandas.apply 진행률 표시를 위함

# --- 1. 설정 (Configuration) ---
INPUT_FILENAME = "news_test.csv"
OUTPUT_FILENAME = "news_classified_results_summary_individual.csv"
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
    auto_tqdm.pandas(desc="개별 기사 요약 중") # tqdm.pandas() 활성화
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
    df.reset_index(drop=True, inplace=True) # 그룹화를 위해 인덱스 재설정
    print(f"✅ 총 {len(df)}개의 고유한 뉴스 기사를 준비했습니다.")
    return df

def cluster_articles(df: pd.DataFrame) -> pd.DataFrame:
    """SentenceTransformer를 사용하여 기사들을 의미 기반으로 그룹화합니다."""
    print(f"\n2단계: '{EMBEDDING_MODEL_NAME}' 모델로 기사 그룹화...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    embeddings = model.encode(df['content'].tolist(), show_progress_bar=True)
    
    clusters = util.community_detection(embeddings, min_community_size=3, threshold=0.5)
    
    doc_id_to_cluster_id = {doc_id: i for i, cluster in enumerate(clusters) for doc_id in cluster}
    
    df['cluster_id'] = df.index.map(lambda x: doc_id_to_cluster_id.get(x, -1))
    print(f"✅ {len(clusters)}개의 의미 있는 그룹을 발견했습니다.")
    return df

# [수정] 3단계: 토픽 분류 (프롬프트 고도화)
def classify_clusters(df: pd.DataFrame, model: genai.GenerativeModel, categories: List[str]) -> Dict[int, str]:
    """그룹화된 기사들을 Gemini API를 통해 주어진 카테고리로 분류합니다."""
    print("\n3단계: Gemini API로 각 그룹의 토픽 분류...")
    topic_map = {}
    
    valid_clusters = [c for c in df['cluster_id'].unique() if c != -1]

    for cluster_id in tqdm(valid_clusters, desc="그룹 토픽 분류 중"):
        try:
            cluster_df = df[df['cluster_id'] == cluster_id]
            sample_titles = cluster_df.head(5)['title'].tolist()
            titles_str = "\n".join([f"- {title}" for title in sample_titles])

            category_list_str = f"[{', '.join(categories)}]"
            
            # [프롬프트 고도화] 취업준비생을 위한 페르소나 및 목적 부여
            classification_prompt = (
                f"당신은 취업 준비생의 면접 준비를 돕는 전문 커리어 애널리스트입니다.\n"
                f"아래는 지원자가 관심 있는 기업의 최신 뉴스 제목들입니다. "
                f"이 기사들의 핵심 주제를 파악하여, 지원자가 자기소개서나 면접에서 활용할 수 있도록 "
                f"주어진 '직무/산업 토픽 목록'에서 가장 적합한 카테고리 하나만 골라주세요.\n\n"
                f"대답은 모두 존댓말로 합니다.\n\n"
                f"--- 직무/산업 토픽 목록 ---\n{category_list_str}\n\n"
                f"--- 기사 제목 목록 ---\n{titles_str}\n\n"
                f"가장 적합한 토픽 (목록에서 하나만 선택): "
            )
            
            classification_response = model.generate_content(classification_prompt)
            found_category = next((cat for cat in categories if cat in classification_response.text), "분류 실패")
            topic_map[cluster_id] = found_category

        except Exception as e:
            print(f"  - 클러스터 {cluster_id} 처리 중 API 오류: {e}")
            topic_map[cluster_id] = "API 오류"
            
    return topic_map

# [신규] 4단계: 개별 기사 요약
def generate_individual_summaries(df: pd.DataFrame, model: genai.GenerativeModel) -> pd.DataFrame:
    """
    모든 개별 기사에 대해 고유한 요약문을 생성합니다.
    [주의] 이 함수는 기사 N개에 대해 N번의 API 호출을 실행합니다.
    """
    print(f"\n4단계: Gemini API로 {len(df)}개의 개별 기사 요약 생성...")
    
    def get_summary(content: str) -> str:
        """단일 기사 본문을 받아 요약문을 반환하는 함수"""
        try:
            # [프롬프트 고도화] 취업준비생을 위한 'So What' 관점의 요약 지시
            summary_prompt = (
                f"당신은 취업 준비생의 면접 준비를 돕는 전문 커리어 애널리스트입니다.\n"
                f"다음 뉴스 기사 본문을 읽고, 이 뉴스가 지원자에게 어떤 의미가 있는지(예: 회사의 성장 동력, 직면한 위기, 인재상 변화 등)에 초점을 맞춰 "
                f"핵심 내용을 2-3문장으로 요약해주세요.\n\n"
                f"대답은 모두 존댓말로 합니다.\n\n"
                f"**[중요 지시] 응답은 어떠한 머리말, 인사, 또는 '요약:'과 같은 접두사도 붙이지 말고, 순수한 2-3문장의 요약 내용으로 즉시 시작해야 합니다.**\n\n"
                f"--- 기사 본문 ---\n{content}\n\n"
                f"요약:"
            )
            response = model.generate_content(summary_prompt)
            return response.text.strip()
        except Exception as e:
            return f"요약 중 오류 발생: {e}"

    # .progress_apply()를 사용하여 진행률 표시줄과 함께 모든 행에 함수 적용
    df['summary'] = df['content'].progress_apply(get_summary)
    return df

def main():
    """메인 실행 함수"""
    gemini_model = setup_gemini()
    df = load_and_preprocess_data(INPUT_FILENAME)
    df_clustered = cluster_articles(df)
    
    # 3단계: 토픽 분류
    topic_map = classify_clusters(df_clustered, gemini_model, TOPIC_CATEGORIES)
    df_clustered['topic'] = df_clustered['cluster_id'].map(topic_map).fillna('기타')
    
    # 4단계: 개별 기사 요약
    df_final = generate_individual_summaries(df_clustered, gemini_model)
    
    df_final.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
    
    print(f"\n🎉 모든 분석이 완료되었습니다! 결과가 '{OUTPUT_FILENAME}' 파일에 저장되었습니다.")
    print("\n--- 최종 토픽 분류 요약 ---")
    print(df_final['topic'].value_counts())

if __name__ == "__main__":
    main()
