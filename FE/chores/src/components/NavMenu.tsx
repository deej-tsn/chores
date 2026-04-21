import { UserContext } from "@/context/UserContext";
import { fetchURL } from "@/utils/fetch";
import { useContext} from "react";
import { useNavigate } from "react-router";

export default function NavMenu() {
    const navigate = useNavigate();
    const { setUser } = useContext(UserContext);

    async function logout(navigate: any) {
        try {
            const response = await fetch(fetchURL("/logout"), {
                method: "GET",
                credentials: "include",
            });

            if (response.ok) {
                console.log("Logged out successfully");
                setUser(undefined);
                navigate("/login");
            } else {
                console.error("Failed to log out");
            }
        } catch (error) {
            console.error("Error during logout:", error);
        }
    }

    return ( 
        <div className="absolute right-0 mt-2 w-40 bg-white rounded-xl shadow-lg py-2 text-black">
            <button className="w-full text-left px-4 py-2 hover:bg-gray-100" onClick={() =>logout(navigate)}>
                Logout
            </button>
        </div>
)}