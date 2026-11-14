import { Link, useLocation } from "react-router";

interface NavLinkProps {
  path: string;
  label: string;
}

export default function NavLink({ path, label }: NavLinkProps) {
  const location = useLocation();
  // Prefix-with-slash, not a bare startsWith: "/home" must not match
  // "/home-chores", and "chores/home" must not stay lit on a sibling route.
  const isActive =
    location.pathname === path || location.pathname.startsWith(`${path}/`);

  const baseClasses =
    "p-2 rounded-4xl mx-2 font-bold transition-colors duration-200 text-gray-100";
  const activeClasses = "bg-amber-700";
  const inactiveClasses = "hover:bg-amber-600";

  return (
    <Link
      to={path}
      className={`${baseClasses} ${isActive ? activeClasses : inactiveClasses}`}
    >
      {label}
    </Link>
  );
}
