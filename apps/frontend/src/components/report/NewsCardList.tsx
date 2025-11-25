import NewsCard from "./NewsCard";

export default function NewsCardLIst() {
  return (
    <div className="flex flex-col gap-2">
      <NewsCard />
      <NewsCard />
      <NewsCard />
    </div>
  );
}
