import { useContext } from "react";
import { editPanelContext } from "../context/EditContext";
import { UserContext } from "../context/UserContext";

interface DayCellProps {
  day: string;
  time: "Morning" | "Evening";
  assigned: string | undefined;
  id: number;
  bgAssigned?: string; // optional props for theme
  bgEmpty?: string;
  textColor?: string;
}

export default function DayCell({
  day,
  time,
  assigned,
  id,
  bgAssigned = "#FFE8C4",
  bgEmpty = "#FFF8F2",
  textColor = "#3A2F2F",
}: DayCellProps) {
  const { setEditPanelState } = useContext(editPanelContext);
  const { user } = useContext(UserContext);

  function editDay() {
    if (!assigned || user?.first_name === assigned) setEditPanelState(id);
  }

  return (
    <div
      onClick={editDay}
      className={`
        w-full h-full rounded-2xl p-3 flex flex-col items-center justify-center font-bold cursor-pointer
        transition-colors duration-200 ease-in-out
        ${assigned ? "shadow-md" : "shadow-sm hover:shadow-md"}
      `}
      style={{
        backgroundColor: assigned ? bgAssigned : bgEmpty,
        color: textColor,
      }}
    >
      <h1 className="text-sm md:text-base">{`${day} - ${time}`}</h1>
      <h2 className="text-sm md:text-base font-medium">
        {assigned ?? "Unassigned"}
      </h2>
    </div>
  );
}