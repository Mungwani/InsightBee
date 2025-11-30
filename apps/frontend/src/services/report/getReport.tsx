// src/service/newsService.ts

/** 📌 뉴스 가져오기 API */
export const fetchNewsByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);
    const response = await fetch(
      `http://127.0.0.1:8000/api/report/news?company_name=${encodedName}&sort_order=newest`
    );
    if (!response.ok) {
      throw new Error("뉴스 데이터를 가져오는데 실패했습니다.");
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    throw error;
  }
};

/** 📌 Summary(핵심요약) 가져오기 API */
export const fetchSummaryByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);
    const response = await fetch(
      `http://127.0.0.1:8000/api/report/summary?company_name=${encodedName}`
    );

    if (!response.ok) {
      throw new Error("요약 데이터를 가져오는데 실패했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error(error);
    throw error;
  }
};
