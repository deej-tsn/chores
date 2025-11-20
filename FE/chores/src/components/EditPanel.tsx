import { useContext } from "react";
import { editPanelContext } from "../context/EditContext";
import { convertDataToTimeTableType, type TimeTableDict } from "../utils/timetable";
import { UserContext } from "../context/UserContext";
import { MdCancel } from "react-icons/md";
import { fetchURL } from "@/utils/fetch";

interface EditPanelProps {
  setTimetable: (data: TimeTableDict) => void;
}

export default function EditPanel({ setTimetable }: EditPanelProps) {
  const { showEditPanel, setEditPanelState } = useContext(editPanelContext);
  const { user } = useContext(UserContext);

  async function patchDay(event: React.FormEvent) {
    event.preventDefault();
    const formData = new FormData(event.target as HTMLFormElement);

    let data: { dayID: number; assign_to_self?: boolean } = {
      dayID: showEditPanel ?? -1,
    };

    if (formData.get("assign") !== "") {
      data = { assign_to_self: true, ...data };
    }

    try {
      const res = await fetch(fetchURL('/timetable'), {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const updatedData = await res.json();
      setTimetable(convertDataToTimeTableType(updatedData));
      setEditPanelState(undefined);
    } catch (err) {
      console.error(err);
    }
  }

  if (!showEditPanel) return null;

  return (
    <>
      {/* Backdrop */}
        <div className="fixed top-0 left-0 w-screen h-screen z-10 backdrop-blur-sm bg-black/20"></div>

      {/* Panel */}
      <div className="z-20 w-11/12 md:w-96 h-fit fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-3xl shadow-xl p-6 animate-fadeIn flex flex-col gap-4">
        {/* Close button */}
        <button
          className="self-end text-2xl text-[#E59D50] font-bold hover:text-[#FFB974] transition-colors"
          onClick={() => setEditPanelState(undefined)}
        >
          <MdCancel />
        </button>

        {/* Form */}
        <form className="flex flex-col items-center gap-4 w-full" onSubmit={patchDay}>
          <div className="flex flex-col w-full items-center gap-2">
            <h1 className="text-xl font-bold text-[#3A2F2F]">Assign To:</h1>
            <select
              id="assign"
              name="assign"
              className="w-full bg-[#FFF8F2] text-[#3A2F2F] py-2 px-3 rounded-2xl border border-[#FFD7A8] cursor-pointer focus:outline-none focus:border-[#E59D50] transition-colors"
            >
              <option value="">Unassigned</option>
              <option value={user?.first_name}>{user?.first_name}</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full bg-[#FFB974] text-[#3A2F2F] font-bold py-2 rounded-2xl shadow-md hover:bg-[#E59D50] hover:text-[#FFF8F2] transition-colors"
          >
            Update
          </button>
        </form>
      </div>
    </>
  );
}
