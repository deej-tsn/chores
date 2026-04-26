import type { User } from "@/types/user";
import NavLink from "./NavLink";
import { useState } from "react";
import NavMenu from "./NavMenu";

interface NavbarProps {
  user: User;
}

const displayUserName = (user: User) =>
  (user.first_name.charAt(0) + user.second_name.charAt(0)).toUpperCase();

export default function Navbar({ user }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="w-11/12 h-16 p-2 max-w-full rounded-3xl shadow-lg fixed top-5 bg-[#e59d50]/70 flex z-20 backdrop-blur-lg">
      {/* Left Page Options */}
      <div className="h-full flex items-center grow gap-4">
        <NavLink path="/home" label="Home" />
        {user.role == "admin" && <NavLink path="/stats" label="Stats" />}
      </div>
      {/* Right User Profile */}
      <div className="relative">
        <div
          id="userProfile"
          onClick={() => setMenuOpen((prev) => !prev)}
          className="h-full aspect-square rounded-full flex items-center justify-center bg-[#FFB974] cursor-pointer transition-colors hover:bg-transparent font-bold text-[#FFF8F2]"
        >
          {displayUserName(user)}
        </div>
        {menuOpen && <NavMenu />}
      </div>
    </nav>
  );
}
