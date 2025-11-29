// src/service/newsService.ts
export const fetchNewsByCompany = async (companyName: string) => {
  try {
    const encodedName = encodeURIComponent(companyName);
    console.log(encodedName);
    const response = await fetch(
      `http://127.0.0.1:8000/api/report/news?company_name=${encodedName}&sort_order=newest`
    );
    if (!response.ok) {
      throw new Error("뉴스 데이터를 가져오는데 실패했습니다.");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
