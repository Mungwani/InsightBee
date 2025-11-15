import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from kiwipiepy import Kiwi
import warnings

# --- 0. 초기 설정 ---
# 불필요한 경고 메시지를 숨기기
warnings.filterwarnings("ignore")

# --- 1. 데이터 로딩 및 전처리 ---
print("CSV 파일을 로딩합니다...")
try:
    df = pd.read_csv("news.csv", encoding='utf-8-sig')
except FileNotFoundError:
    print("오류: 'news.csv' 파일을 찾을 수 없습니다.")
    print("스크립트와 같은 폴더에 파일이 있는지 확인해주세요.")
    exit()

print(f"파일에서 읽어온 원본 열 이름: {df.columns.tolist()}")

# CSV 파일의 열 이름에 있을 수 있는 좌우 공백을 제거
df.columns = df.columns.str.strip()

# '본문' 열의 이름을 'content'로 통일
if '본문' in df.columns and 'content' not in df.columns:
    df.rename(columns={'본문': 'content'}, inplace=True)

# '제목' 열의 이름을 'title'로 통일
if '제목' in df.columns and 'title' not in df.columns:
    df.rename(columns={'제목': 'title'}, inplace=True)

# --- 강화된 오류 진단 로직 ---
# 분석에 필요한 'content'와 'title' 열이 있는지 최종 확인
required_cols = ['title', 'content']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print("-" * 50)
    print(f"오류: 필수 열을 찾을 수 없습니다: {', '.join(missing_cols)}")
    print("CSV 파일에 '제목'과 '본문' 열이 올바르게 포함되어 있는지 확인해주세요.")
    print(f"스크립트가 인식한 현재 열 목록: {df.columns.tolist()}")
    print("-" * 50)
    exit()


# 'content' 또는 'title' 열에 비어있는 데이터 제거
df.dropna(subset=['content', 'title'], inplace=True)

# --- 중복 뉴스 기사 제거 (제목 기준) ---
initial_count = len(df)
df.drop_duplicates(subset=['title'], keep='first', inplace=True)
final_count = len(df)
print(f"중복 뉴스 {initial_count - final_count}개를 제거했습니다.")

documents = df['content'].astype(str).tolist()
print(f"총 {len(documents)}개의 고유한 뉴스 기사를 분석합니다.")


# --- 2. BERTopic으로 전체 뉴스 토픽 분석 ---
print("\nBERTopic 분석을 시작합니다... (시간이 소요될 수 있습니다)")
# 한국어 문장 임베딩에 특화된 모델 로드
embedding_model = SentenceTransformer('jhgan/ko-sbert-nli')

# BERTopic 모델 초기화 (min_topic_size는 토픽으로 인정할 최소 문서 수)
topic_model = BERTopic(embedding_model=embedding_model,
                        min_topic_size=5,
                        verbose=True)

# 모델 학습 및 토픽 할당
topics, _ = topic_model.fit_transform(documents)

# <<핵심 로직>>: 분석된 토픽 결과를 'topic_num'이라는 새 열에 추가
df['topic_num'] = topics
print("BERTopic 분석 및 토픽 열 추가 완료!")


# --- 3. 개별 뉴스 키워드 추출 (KeyBERT 사용) ---
print("\n개별 뉴스에 대한 키워드 추출을 시작합니다...")
kw_model = KeyBERT(embedding_model)
kiwi = Kiwi()

def extract_keywords_keybert(text, num_keywords=5):
    """Kiwi로 명사를 추출하고 KeyBERT로 핵심 키워드를 찾는 함수"""
    try:
        nouns = " ".join([token.form for token in kiwi.analyze(text)[0][0] if token.tag in ['NNG', 'NNP']])
        if not nouns:
            return ""
        keywords = kw_model.extract_keywords(nouns, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=num_keywords)
        return ", ".join([f"#{kw[0]}" for kw in keywords])
    except Exception as e:
        print(f"키워드 추출 중 오류 발생: {e}")
        return ""

# 'keywords'라는 새 열에 추출된 키워드를 추가합니다.
df['keywords'] = df['content'].apply(extract_keywords_keybert)
print("키워드 추출 및 열 추가 완료!")


# --- 4. 최종 결과 저장 및 요약 출력 ---
output_filename = "news_analysis_results.csv"
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"\n✅ 모든 분석이 완료되었습니다. 결과가 '{output_filename}' 파일에 저장되었습니다.")
print("\n--- BERTopic 주요 토픽 요약 ---")
# 토픽의 대표 단어들과 함께 정보 출력
topic_infos = topic_model.get_topic_info()
print(topic_infos.head(11))