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
        <div className="w-screen min-h-screen bg-[#FFF8F2] flex flex-col items-center">
            <Navbar user={user} />
            <main className="w-full mt-24 p-4 gap-6">
                <Outlet />
            </main>
        </div>
    ) 
};