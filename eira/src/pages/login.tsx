import { useEffect } from "react";
import type { UserDataT } from "../types/responses";
import { useLocation } from "wouter";
import { useCookies } from 'react-cookie'


function LoginPage() {
    const [, navigate] = useLocation();
    const [cookies, , removeCookie] = useCookies(["session"])

    async function fetchUser() {
        let resp: Response;

        if (!cookies.session) {
            return
        }

        try {
            resp = await fetch("/users/@me", {"credentials": "include"});
        } catch (error) {
            console.error(error);
            return
        }

        if (!resp.ok) {
            throw new Error(`Unable to fetch user data from API: ${resp.status}`);
        }

        const data: UserDataT = await resp.json()
        if (!data) {
            removeCookie("session", cookies.session);
            return
        }

        return navigate("/");
    }

    useEffect(() => {
        fetchUser();
    }, []);

    return (
        <>
            Login
        </>
    )
}

export default LoginPage