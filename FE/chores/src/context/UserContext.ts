import { createContext, createElement, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { Token, TokenData, User } from "../types/user";

type UserContextType = {
    user: User | undefined;
    setUser: (user: User) => void;
    token : Token | undefined;
    setToken : (token : Token) => void
}

const UserContext = createContext<UserContextType>({
    user: undefined,
    setUser: () => {},
    token : undefined,
    setToken: () => {}
});

function UserProvider({ children }: { children: ReactNode }) {
    
    const [user, setUser] = useState<User | undefined>(undefined);
    const [token, setToken] = useState<Token | undefined>(undefined);
    

    useEffect(() => {
        async function getUserInfo() {
            if(!token) return
            fetch('http://localhost:8000/user',{
                method: 'GET',
                headers : {
                    'Authorization': `Bearer ${token.access_token}`
                }
            }).then((res) => res.json()).then((data : TokenData) => {
                setUser({
                    email : data.sub,
                    first_name: data.first_name,
                    second_name: data.second_name,
                    colour : data.colour
                })
            }).catch((error) => console.error(error))
        }

        getUserInfo()
    }, [token])

    return createElement(
        UserContext.Provider,
        { value: { user, setUser, token, setToken } },
        children
    );
}

export { UserContext, UserProvider };