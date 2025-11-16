import { useContext } from "react"
import { editPanelContext } from "../context/EditContext"
import { convertDataToTimeTableType, type TimeTableDict } from "../utils/timetable"
import { UserContext } from "../context/UserContext"
import { MdCancel } from "react-icons/md";

interface EditPanelProps {
    setTimetable : (data : TimeTableDict) => void
}

export default function EditPanel({setTimetable} : EditPanelProps){
    const {showEditPanel,setEditPanelState} = useContext(editPanelContext)
    const {user} = useContext(UserContext)

    function patchDay(event : React.FormEvent){
        event.preventDefault()
        const formData = new FormData(event.target as HTMLFormElement)
        let data : {dayID : number, assign_to_self? : boolean}=  {dayID : showEditPanel?? -1 }
        if(formData.get('assign') !== ""){
            data = {assign_to_self : true, ...data}
        }
        console.log(data)
        console.log(formData.get('assign'))
        fetch(`https://local.app.com:8000/timetable/`, {
            method: 'PATCH',
            credentials : 'include',
            headers : {
                'Content-Type': 'application/json',
            },
            body : JSON.stringify(data)
        }).then(res => {
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return res.json();
        })
        .then(data => {
            const timetable = convertDataToTimeTableType(data);
            setTimetable(timetable);
            setEditPanelState(undefined)
        })
        .catch(console.error);
    }

    if(!showEditPanel) return

    return( 
        <>
            <div className="w-screen h-full backdrop-blur-sm absolute top-0 left-0 z-10"></div>
            <div className="z-20 w-11/12 md:w-96 h-fit absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-amber-500 rounded-4xl drop-shadow-2xl p-5">
                <button className=" cursor-pointer font-bold text-2xl text-amber-50 mb-2 transition-colors hover:text-gray-400" onClick={() => setEditPanelState(undefined)}><MdCancel/></button>
                <form className="w-full flex items-center flex-col" onSubmit={patchDay}>
                    <div className="w-full flex items-center justify-center">
                        <h1 className=" text-xl font-bold text-amber-50">Assign To:</h1>
                        <select className="ml-2 bg-amber-50 cursor-pointer py-1 px-2 rounded-2xl" id='assign' name="assign">
                            <option value="">Unassigned</option>
                            <option value={user?.first_name}>{user?.first_name}</option>
                        </select>
                    </div>
                    <button className=" bg-amber-50 border border-amber-500 text-amber-500 px-5 py-2 rounded-2xl m-2 transition-all font-bold hover:bg-amber-500 hover:border-amber-50 hover:text-amber-50" type="submit">Update</button>
                </form>
            </div>
        </>
    )
}