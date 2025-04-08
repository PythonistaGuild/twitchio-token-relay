import { useEffect } from "react";
import type { UserDataT } from "../types/responses";
import { useLocation } from "wouter";


function LoginPage() {
    const [, navigate] = useLocation();

    async function fetchUser() {
        let resp: Response;

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