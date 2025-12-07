import React, { useMemo } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

type Sentiment = "긍정" | "부정" | "중립";

interface DataItem {
  name: Sentiment;
  value: number;
}

interface DonutChartProps {
  data: readonly DataItem[];
}

const COLORS: Record<Sentiment, string> = {
  긍정: "#34D399", // Soft Emerald
  부정: "#F87171", // Soft Red
  중립: "#94A3B8", // Slate Gray
};

const DonutChart: React.FC<DonutChartProps> = ({ data }) => {

  const { chartData, topItem } = useMemo(() => {
    const total = data.reduce((sum, item) => sum + item.value, 0);

    if (total === 0) return { chartData: [], topItem: null };

    const processedData = data.map((item) => ({
      ...item,
      percent: ((item.value / total) * 100).toFixed(0),
    }));

    const maxItem = processedData.reduce((prev, current) =>
      prev.value > current.value ? prev : current
    );

    return { chartData: processedData, topItem: maxItem };
  }, [data]);

  if (!topItem) return <div className="text-gray-400 text-sm">데이터 없음</div>;

  // 값이 0보다 큰 항목만 필터링하여 렌더링 데이터로 사용
  const renderData = chartData.filter(item => item.value > 0);

  // 필터링 후 데이터가 없으면 데이터 없음 표시 (총합이 0이 아닌데 전부 0일 때 대비)
  if (renderData.length === 0) return <div className="text-gray-400 text-sm">데이터 없음</div>;

  return (
    <div className="flex flex-col items-center justify-center py-4">
      <div className="relative w-[220px] h-[220px]">
        {/* 도넛 차트 */}
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={renderData} // <<< 필터링된 데이터 사용
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={90}
              paddingAngle={3} // <<< paddingAngle은 그대로 유지
              dataKey="value"
              cornerRadius={6}
              stroke="none"
            >
              {renderData.map((entry, index) => ( // <<< 필터링된 데이터 매핑
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[entry.name]}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-xs text-gray-400 font-medium mb-1">주요 여론</span>
          <p
            className="text-3xl font-extrabold tracking-tight"
            style={{ color: COLORS[topItem.name] }}
          >
            {topItem.name}
          </p>
          <span className="text-sm text-gray-500 font-semibold mt-1">
            {topItem.percent}%
          </span>
        </div>
      </div>

      <div className="flex justify-center gap-4 mt-2">
        {/* 범례는 전체 데이터를 보여줍니다. */}
        {chartData.map((item) => (
          <div
            key={item.name}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-50 border border-gray-100 shadow-sm"
          >
            <span
              className="w-2.5 h-2.5 rounded-full ring-2 ring-white"
              style={{ backgroundColor: COLORS[item.name] }}
            ></span>
            <span className="text-xs font-semibold text-gray-600">
              {item.name}
            </span>
            <span className="text-xs text-gray-400 font-medium">
              {item.percent}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DonutChart;