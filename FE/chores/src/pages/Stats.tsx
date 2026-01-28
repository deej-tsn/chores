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

const COLOURS = [
  "#64748b", // slate
  "#7c3aed", // muted violet
  "#6366f1", // soft indigo
  "#0ea5e9", // muted sky
  "#14b8a6", // muted teal
  "#22c55e", // soft green
  "#f59e0b", // muted amber
];

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
		<h1 className=" text-center font-medium text-2xl">Number Of Shifts </h1>
        {loading && <div>Loading…</div>}
        {error && <div>{error}</div>}
        {data && <Bar data={data} options={chartOptions} />}
      </Card>
    </div>
  );
}

function formatChartData(data: CountResponse): ChartData<"bar"> {
  	const entries = Object.entries(data)
    .sort(([, a], [, b]) => b - a);

	const counts = entries.map(([, count]) => count);
	return {
		labels: entries.map(([name]) => name),
		datasets: [
		{
			label: "Count",
			data: counts,
			backgroundColor: entries.map(
				(_, i) => COLOURS[i % COLOURS.length]
			),
		},
		],
	};
}

const chartOptions: ChartOptions<"bar"> = {
	indexAxis: "y",
	responsive: true,
	plugins: {
		legend: {
			display: false,
		},
	},
	scales: {
		y: {
			title: {
				display: true,
				text: "People",
			},
			beginAtZero: true,
			ticks: {
				precision: 0, // 👈 forces integers
			},
		},
		x: {
			title: {
				display: true,
				text: "Number of visits"
			}
		}
	},
};