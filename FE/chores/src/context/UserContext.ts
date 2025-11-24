import { createContext, createElement, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { TokenData, User } from "../types/user";
import { fetchURL } from "@/utils/fetch";

type UserContextType = {
  user: User | undefined;
  setUser: (user: User) => void;
  token: boolean | undefined;
  setToken: (token: boolean) => void;
};

const UserContext = createContext<UserContextType>({
  user: undefined,
  setUser: () => {},
  token: undefined,
  setToken: () => {},
});

function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | undefined>(undefined);
  const [token, setToken] = useState<boolean>(false);

  useEffect(() => {
    async function getUserInfo() {
      try {
        const res = await fetch(fetchURL("/user"), {
          method: "GET",
          credentials: "include", // ensures cookie is sent
        });

        if (!res.ok) {
          throw new Error("Not authorized");
        }

        const data: TokenData = await res.json();

        setUser({
          email: data.sub,
          first_name: data.first_name,
          second_name: data.second_name,
          colour: data.colour,
        });
      } catch (error) {
        console.error("Failed to fetch user info:", error);
        setUser(undefined);
      }
    }

    getUserInfo();
  }, [token]);

  return createElement(
    UserContext.Provider,
    { value: { user, setUser, token, setToken } },
    children,
  );
}

export { UserContext, UserProvider };
