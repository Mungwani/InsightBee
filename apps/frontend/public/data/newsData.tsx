//////////////////////////////////////워드 클라우드 목 데이터///////////////////////////////////////////
export interface WordData {
  text: string;
  value: number;
  sentiment: "positive" | "negative";
  description: string;
  news: number;
}

export const sentimentWords: WordData[] = [
  {
    text: "주식",
    value: 50,
    sentiment: "positive",
    description: "토픽 요약1",
    news: 84,
  },
  {
    text: "오른다",
    value: 40,
    sentiment: "positive",
    description: "토픽 요약2",
    news: 62,
  },
  {
    text: "화이팅",
    value: 35,
    sentiment: "positive",
    description: "토픽 요약3",
    news: 15,
  },
  {
    text: "가즈아",
    value: 25,
    sentiment: "positive",
    description: "토픽 요약4",
    news: 55,
  },
  {
    text: "화성",
    value: 20,
    sentiment: "positive",
    description: "토픽 요약5",
    news: 32,
  },
  // 부정
  {
    text: "으아ㅏ악",
    value: 45,
    sentiment: "negative",
    description: "토픽 요약6",
    news: 45,
  },
  {
    text: "그만",
    value: 40,
    sentiment: "negative",
    description: "토픽 요약7",
    news: 16,
  },
  {
    text: "떨어져",
    value: 35,
    sentiment: "negative",
    description: "토픽 요약8",
    news: 27,
  },
  //   {
  //     text: "제발",
  //     value: 25,
  //     sentiment: "negative",
  //     description: "토픽 요약9",
  //     news: 223,
  //   },
  //   {
  //     text: "물타기",
  //     value: 20,
  //     sentiment: "negative",
  //     description: "토픽 요약10",
  //     news: 2,
  //   },
];
//////////////////////////////////////뉴스 목 데이터///////////////////////////////////////////
export interface newsData {
  title: string;
  sentiment: "positive" | "negative";
  summary: string;
  media: string;
  day: string;
  topic: string;
  link: string;
}

export const news: newsData[] = [
  {
    title: "삼성전자, 3분기 실적 예상치 상회…반도체 회복 본격화",
    sentiment: "positive",
    summary:
      "삼성전자가 3분기 영업이익 9조 원을 기록하며 시장 기대를 넘어섰다. 반도체 수요가 회복세를 보이며 실적 개선을 견인했다.",
    media: "연합뉴스",
    day: "2025-10-22",
    topic: "경제",
    link: "https://news.example.com/samsung-earnings",
  },
  {
    title: "LG화학, 배터리 원가 상승 여파로 실적 부진",
    sentiment: "negative",
    summary:
      "원재료 가격 상승과 글로벌 수요 둔화로 인해 LG화학의 배터리 부문 수익성이 하락했다.",
    media: "한국경제",
    day: "2025-10-21",
    topic: "산업",
    link: "https://news.example.com/lgchem-decline",
  },
  {
    title: "코스피, 미국 금리 동결 소식에 1% 상승 마감",
    sentiment: "positive",
    summary:
      "미국 연준이 금리를 동결하면서 투자심리가 개선되어 코스피 지수가 상승 마감했다.",
    media: "매일경제",
    day: "2025-10-20",
    topic: "증시",
    link: "https://news.example.com/kospi-rise",
  },
  {
    title: "서울 전셋값 3개월 연속 상승…전세난 우려 커져",
    sentiment: "negative",
    summary:
      "서울 주요 지역의 전셋값이 꾸준히 상승하면서 서민들의 주거 부담이 커지고 있다.",
    media: "서울신문",
    day: "2025-10-19",
    topic: "부동산",
    link: "https://news.example.com/seoul-rent",
  },
  {
    title: "현대차, 전기차 판매량 사상 최고치 기록",
    sentiment: "positive",
    summary:
      "아이오닉 시리즈의 글로벌 판매가 호조를 보이며 현대차가 전기차 시장 점유율을 확대했다.",
    media: "조선비즈",
    day: "2025-10-18",
    topic: "자동차",
    link: "https://news.example.com/hyundai-ev",
  },
  {
    title: "국내 소비심리 4개월 만에 하락 전환",
    sentiment: "negative",
    summary:
      "물가 상승과 경기 불확실성으로 인해 국내 소비심리지수가 4개월 만에 하락세로 돌아섰다.",
    media: "한겨레",
    day: "2025-10-17",
    topic: "경제",
    link: "https://news.example.com/consumer-sentiment",
  },
  {
    title: "AI 스타트업 ‘딥마인드코리아’, 시리즈B 투자 유치 성공",
    sentiment: "positive",
    summary:
      "딥러닝 기반 솔루션을 개발하는 딥마인드코리아가 300억 원 규모의 시리즈B 투자를 유치했다.",
    media: "테크M",
    day: "2025-10-16",
    topic: "IT",
    link: "https://news.example.com/deepmindkorea",
  },
  {
    title: "국제 유가 급등…물가 부담 다시 커진다",
    sentiment: "negative",
    summary:
      "중동 지역의 긴장 고조로 국제 유가가 급등하면서 전 세계 물가 상승 압력이 커지고 있다.",
    media: "SBS 뉴스",
    day: "2025-10-15",
    topic: "국제",
    link: "https://news.example.com/oil-price",
  },
  {
    title: "카카오, 새로운 AI 번역 서비스 출시",
    sentiment: "positive",
    summary:
      "카카오가 실시간 다국어 번역 기능을 갖춘 새로운 AI 서비스를 공개해 시장의 주목을 받고 있다.",
    media: "ZDNet Korea",
    day: "2025-10-14",
    topic: "IT",
    link: "https://news.example.com/kakao-ai",
  },
  {
    title: "전국 미세먼지 ‘나쁨’ 수준…야외활동 주의 필요",
    sentiment: "negative",
    summary:
      "대기 정체로 전국 대부분 지역에서 미세먼지 농도가 ‘나쁨’ 수준을 보이고 있다.",
    media: "YTN",
    day: "2025-10-13",
    topic: "환경",
    link: "https://news.example.com/fine-dust",
  },
];
