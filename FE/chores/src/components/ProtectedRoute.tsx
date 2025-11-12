import { Navigate, Outlet } from "react-router";
import { useContext } from "react";
import { UserContext } from "../context/UserContext";
import Navbar from "./Navbar";

type ProtectedRouteProps = {
  redirectPath?: string;
};

export default function ProtectedRoute({ redirectPath = "/login" }: ProtectedRouteProps) {
    const {user} = useContext(UserContext)

    if (!user) {
        return <Navigate to={redirectPath} replace />;
    }

    return (
        <div className=' w-screen h-screen bg-amber-50 items-center justify-center relative flex flex-col'>
            <Navbar user={user}/>

            <Outlet/>
        </div>
    ) 
};