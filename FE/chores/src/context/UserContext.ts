import { createContext, createElement, useState } from "react";
import type { ReactNode } from "react";

type User = {
    first_name: string;
    second_name: string;
    email: string;
    colour: string;
}

type UserContextType = {
    user: User | undefined;
    setUser: (user: User) => void;
}

const UserContext = createContext<UserContextType>({
    user: undefined,
    setUser: () => {}
});

function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | undefined>(undefined);

    return createElement(
        UserContext.Provider,
        { value: { user, setUser } },
        children
    );
}

export { UserContext, UserProvider };