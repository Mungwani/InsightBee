import { PieChart, Pie, Cell } from "recharts";

type Sentiment = "긍정" | "부정" | "중립";

interface DataItem {
  name: Sentiment;
  value: number;
}

interface DonutChartProps {
  data: readonly DataItem[];
}

const COLORS: Record<Sentiment, string> = {
  긍정: "#00C851", // 초록
  부정: "#ff4444", // 빨강
  중립: "#9e9e9e", // 회색
};

const DonutChart: React.FC<DonutChartProps> = ({ data }) => {
  // ✅ 비율 계산
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const chartData = data.map((item) => ({
    ...item,
    percent: ((item.value / total) * 100).toFixed(0),
  }));

  // ✅ 가장 비율 높은 항목 찾기
  const topLabel = data.reduce((a, b) => (a.value > b.value ? a : b)).name;

  return (
    <div>
      <div className="relative flex flex-col items-center justify-center">
        {/* 도넛 차트 */}
        <PieChart width={220} height={220}>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            dataKey="value"
            paddingAngle={2}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
            ))}
          </Pie>
        </PieChart>

        {/* 중앙 텍스트 */}
        <div className="absolute text-center">
          <p
            className="text-2xl font-bold "
            style={{ color: COLORS[topLabel] }}
          >
            {topLabel}
          </p>
        </div>
      </div>
      {/* 범례 */}
      <div className="flex gap-4 mt-4 text-sm text-black">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center gap-1">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: COLORS[item.name] }}
            ></span>
            <span>
              {item.name} {item.percent}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DonutChart;
