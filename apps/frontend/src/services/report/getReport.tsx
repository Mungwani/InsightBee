// src/service/newsService.ts

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://insightbee-backend-950949202751.europe-west1.run.app';

/** 뉴스 가져오기 API */
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

/** Summary(핵심요약) 가져오기 API */
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
