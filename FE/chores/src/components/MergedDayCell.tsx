import { useContext } from "react";
import { editPanelContext } from "../context/EditContext";
import { UserContext } from "../context/UserContext";

interface Shift {
  id: number;
  assignee?: string;
}

interface MergedDayCellProps {
  day: string;
  morning: Shift;
  evening: Shift;
  bgAssigned?: string;
  bgEmpty?: string;
  textColor?: string;
}

export default function MergedDayCell({
  day,
  morning,
  evening,
  bgAssigned = "#FFE8C4",
  bgEmpty = "#FFF8F2",
  textColor = "#3A2F2F",
}: MergedDayCellProps) {
  const { setEditPanelState } = useContext(editPanelContext);
  const { user } = useContext(UserContext);

  const isAssigned = morning.assignee || evening.assignee;

  const morningBG = morning.assignee ? "#ffd7a1" : "transparent";
  const eveningBG = evening.assignee ? "#ffd7a1" : "transparent";

  const isAuthorized = ["admin", "user"].includes(user?.role ?? "");

  function canEdit(shift: Shift) {
    return !shift.assignee || shift.assignee === user?.first_name;
  }

  function handleClick(shiftTime : 'Morning' | 'Evening' , shift: Shift) {
    if(!["admin", "user"].includes(user?.role ?? "")) return
    if (canEdit(shift)) setEditPanelState({
        id: shift.id,
        dayOfWeek : day,
        shift : shiftTime
    });
  }

  const getCellClasses = 
  `
      flex-1 flex flex-col justify-center items-center text-center
      transition-all duration-200 rounded-md
      ${isAuthorized ? "cursor-pointer hover:bg-black/10" : "cursor-default"}
  `;


  return (
    <div
      className="
        w-full h-full rounded-2xl p-3 flex flex-col shadow-md border
      "
      style={{
        backgroundColor: isAssigned ? bgAssigned : bgEmpty,
        color: textColor,
        borderColor: "#e5ddd5",
      }}
    >
      <h1 className="text-base font-bold pb-2 text-center">{day}</h1>

      <div
        className="
          flex-1 flex 
          flex-row md:flex-col 
          gap-1
        "
      >
        <div
          onClick={() => handleClick('Morning', morning)}
          className={getCellClasses}
          style={{
            backgroundColor: morningBG,
          }}
        >
          <span className="text-sm font-semibold">Morning</span>
          <span className="text-sm">
            {morning.assignee ?? "Unassigned"}
          </span>
        </div>

        <div
          className="
            bg-[#cfc7c0]
            w-px md:w-full
            h-full md:h-px
          "
        />

        <div
          onClick={() => handleClick('Evening', evening)}
          className={getCellClasses}
          style={{
            backgroundColor: eveningBG,
          }}
        >
          <span className="text-sm font-semibold">Evening</span>
          <span className="text-sm">
            {evening.assignee ?? "Unassigned"}
          </span>
        </div>
      </div>
    </div>
  );
}
