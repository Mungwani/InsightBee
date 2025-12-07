const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://insightbee-950949202751.europe-west1.run.app';

/* 뉴스 가져오기 API */
export const fetchNewsByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);

    const response = await fetch(
      `${BASE_URL}/api/report/news?company_name=${encodedName}&sort_order=newest`
    );

    if (!response.ok) {
      throw new Error("뉴스 데이터를 가져오는데 실패했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error("[fetchNewsByCompany Error]", error);
    throw error;
  }
};

/* Summary(핵심요약) 가져오기 API */
export const fetchSummaryByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);

    const response = await fetch(
      `${BASE_URL}/api/report/summary?company_name=${encodedName}`
    );

    if (!response.ok) {
      throw new Error("요약 데이터를 가져오는데 실패했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error("[fetchSummaryByCompany Error]", error);
    throw error;
  }
};

export const fetchKeywordsByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);

    // [디버깅용 로그 추가]
    console.log("1. 키워드 함수 진입:", companyName);
    console.log("2. 요청할 URL:", `${BASE_URL}/api/analytics/keywords?company_name=${encodedName}`);

    const response = await fetch(
      `${BASE_URL}/api/analytics/keywords?company_name=${encodedName}`
    );

    console.log("3. 응답 도착:", response.status); // 여기까지 찍히는지 확인

    if (!response.ok) {
      throw new Error("키워드 데이터를 가져오는데 실패했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error("[fetchKeywordsByCompany Error]", error);
    throw error;
  }
};


/**
 * 매주 생성되는 주간 리포트(weekly_company_reports) 기반 핵심 정보(Points)를 제공합니다.
 * @param companyName 분석할 기업명
 * @returns { "company_name": string, "points": Array<Object> } 형태의 응답
 */
export const fetchPointsByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);

    const response = await fetch(
      `${BASE_URL}/api/analytics/points?company_name=${encodedName}`
    );

    if (!response.ok) {
      throw new Error("주간 리포트 핵심 정보를 가져오는데 실패했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error("[fetchPointsByCompany Error]", error);
    throw error;
  }
};