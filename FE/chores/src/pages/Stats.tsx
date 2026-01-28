import { Card } from "@/components/ui/card";
import { fetchURL } from "@/utils/fetch";
import { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
);

type CountResponse = Record<string, number>;

export default function StatsPage() {

  const [data, setData] = useState<ChartData<"bar"> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function getChartData() {
      try {
        const url = fetchURL("/count");
        const res = await fetch(url, {
          method: "GET",
          credentials: "include",
        });

        const resData: CountResponse = await res.json();

        if (!res.ok) {
          throw new Error(resData as unknown as string);
        }

        setData(formatChartData(resData));
      } catch (err) {
        setError("An error has occurred");
      } finally {
        setLoading(false);
      }
    }

    getChartData();
  }, []);



  return (
    <div className="w-full flex flex-col items-center gap-6 animate-fade-up animate-duration-500 animate-ease-in-out">
      <Card className="w-full max-w-5xl bg-white rounded-3xl shadow-xl p-6 relative">
        {loading && <div>Loading…</div>}
        {error && <div>{error}</div>}
        {data && <Bar data={data} options={chartOptions} />}
      </Card>
    </div>
  );
}

function formatChartData(data: CountResponse): ChartData<"bar"> {
  const entries = Object.entries(data);

  return {
    labels: entries.map(([name]) => name),
    datasets: [
      {
        label: "Count",
        data: entries.map(([, count]) => count),
      },
    ],
  };
}

const chartOptions: ChartOptions<"bar"> = {
  responsive: true,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0, // 👈 forces integers
      },
    },
  },
};