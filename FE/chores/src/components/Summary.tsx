import type { TimeTableDict, Day } from "@/utils/timetable";

export default function SummaryBox({ timetable }: { timetable: TimeTableDict }) {
  const summary_data: Record<string, number> = {};

  function getAssignee(day: Day): string {
    return day.assignee ?? "Unassigned";
  }

  Object.values(timetable).forEach((value) => {
    const morning = getAssignee(value.Morning);
    const evening = getAssignee(value.Evening);

    summary_data[morning] = (summary_data[morning] ?? 0) + 1;
    summary_data[evening] = (summary_data[evening] ?? 0) + 1;
  });

  return (
    <div className=" absolute -translate-x-1/2 md:translate-x-0 md:left-0 top-10 sm:right-2 bg-[#fff8f2] w-56 sm:w-64 max-h-64 p-4 rounded-2xl shadow-xl z-50 overflow-y-auto border">
      <h2 className="text-base font-semibold mb-2 text-[#3A2F2F]">
        Summary
      </h2>

      <ul className="text-sm space-y-1">
        {Object.entries(summary_data).map(([name, count]) => (
          <li key={name} className="flex justify-between">
            <span>{name}</span>
            <span className="font-medium">{count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
