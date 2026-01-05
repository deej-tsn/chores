import { useContext, useEffect, useState } from "react";
import { UserContext } from "../context/UserContext";
import {
  convertDataToTimeTableType,
  daysOfWeek,
  DefaultTimeTable,
  diffInDates,
  formatDate,
  getMonday,
  type TimetableData,
} from "../utils/timetable";
import luka from "../assets/image.png";
import EditPanel from "../components/EditPanel";
import { Card } from "@/components/ui/card";
import { fetchURL } from "@/utils/fetch";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { isEmpty } from "@/utils/utils";
import MergedDayCell from "@/components/MergedDayCell";

function Home() {
  const { user } = useContext(UserContext);
  const [timetableData, setTimetable] = useState<TimetableData>({
    weekStart: getMonday(),
    timetable: DefaultTimeTable,
  });
  const current_date = new Date()


  async function getTimetable(date?: Date) {
      if(date && diffInDates(date, current_date) > 14){
        alert('Timetable does not exist for given future date')
        return
      }
      const params = date ? `?week=${formatDate(date)}` : "";
      const url = fetchURL(`/timetable${params}`);
      fetch(url, {
        method: "GET",
        credentials: "include",
      })
        .then((res) => res.json())
        .then((data : {weekStart : string, timetable : any[]}) => {
          if(data.timetable.length == 0){
            setTimetable({weekStart: new Date(data.weekStart), timetable : {}})
          } else{
            const newTimetableData = convertDataToTimeTableType(data);
            setTimetable(newTimetableData);
          }

        })
        .catch((error) => console.log(error));
  }

  useEffect(() => {
    getTimetable();
  }, []);


  if (!user) return null;
  let daysToAssign = undefined
  if (!isEmpty(timetableData.timetable)){
    daysToAssign = daysOfWeek.reduce((count, day) => {
    const morning = timetableData.timetable[day].Morning.assignee ? 0 : 1;
    const evening = timetableData.timetable[day].Evening.assignee ? 0 : 1;
    return count + morning + evening;
  }, 0);

  }

  return (
    <>
      <div className="w-full flex flex-col items-center gap-6 animate-fade-up animate-duration-500 animate-ease-in-out">
        {/* Banner */}
        <div className="w-full max-w-4xl flex flex-col md:flex-row items-center gap-4">
          <img src={luka} alt="Luka" className="" />
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl md:text-4xl font-bold text-[#3A2F2F]">
              Hello, {user.first_name}!
            </h1>
            <p className="text-[#6A5F5D] text-md md:text-lg">
              Here's your timetable for the week. Keep those pups happy!
            </p>
          </div>
        </div>

        <Card className="w-full max-w-5xl bg-white rounded-3xl shadow-xl p-6 animate-fade-up animate-duration-500 animate-ease-in-out relative">
            <div className="flex flex-col md:flex-row justify-center mb-6 items-center gap-3 relative">

              {/* NAV BUTTONS */}
              <div className="flex flex-row items-center gap-3 bg-[#FFF8F2] px-4 py-2 rounded-full shadow-sm border border-[#E8D6C5]">
                <Button
                  variant="ghost"
                  className="rounded-full p-2 hover:bg-[#E8D6C5] transition"
                  onClick={() => {
                    const prevWeek = new Date(timetableData.weekStart);
                    prevWeek.setDate(prevWeek.getDate() - 7);
                    getTimetable(prevWeek);
                  }}
                >
                  <ArrowLeft className="w-5 h-5" />
                </Button>

                <h2 className="text-xl font-bold text-[#3A2F2F]">
                  Week: {timetableData.weekStart.toLocaleDateString()}
                </h2>

                <Button
                  variant="ghost"
                  className="rounded-full p-2 hover:bg-[#E8D6C5] transition"
                  onClick={() => {
                    const nextWeek = new Date(timetableData.weekStart);
                    nextWeek.setDate(nextWeek.getDate() + 7);
                    getTimetable(nextWeek);
                  }}
                >
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </div>

              {/* STATUS */}
              {daysToAssign !== undefined && 
                <span className={`text-lg font-semibold ${ daysToAssign > 0 ? "text-[#E59D50]" : "text-[#6A5F5D]"} md:absolute md:right-6`}>
                  {daysToAssign > 0
                    ? `Days to Assign: ${daysToAssign}`
                    : "Fully Allocated"
                  }
                </span>
              }
            </div>
            { !isEmpty(timetableData.timetable) ? 
            <div className="w-full h-fit md:h-64 grid grid-cols-1 grid-rows-7 md:grid-cols-7 md:grid-rows-1 gap-4">
                <>
                  {daysOfWeek.map((day) => (
                    <MergedDayCell
                      key={`${day} - Morning`}
                      day={day}
                      morning={timetableData.timetable[day].Morning}
                      evening={timetableData.timetable[day].Evening}
                    />
                  ))}
                </>
            </div>
            : 
            <div className="w-full h-fit flex justify-center font-bold">No timetable data available</div>
            }
        </Card>
      </div>
      {["admin", "user"].includes(user.role) && <EditPanel week={timetableData.weekStart} setTimetable={setTimetable} />}
    </>
  );
}

export default Home;
