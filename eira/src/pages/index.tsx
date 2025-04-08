import { useEffect, useState } from "react";
import type { UserDataT } from "../types/responses";
import { useLocation } from "wouter";
import "./index.css";
import { useCookies } from "react-cookie";

function Index() {
  const [user, setUser] = useState<UserDataT>();
  const [, navigate] = useLocation();
  const [cookies, , removeCookie] = useCookies(["session"]);

  async function fetchUser() {
    let resp: Response;

    if (!cookies.session) {
      return navigate("/login");
    }

    try {
      resp = await fetch("/users/@me", { credentials: "include" });
    } catch (error) {
      console.error(error);
      return navigate("/login");
    }

    if (!resp.ok) {
      throw new Error(`Unable to fetch user data from API: ${resp.status}`);
    }

    const data: UserDataT = await resp.json();
    if (!data) {
      removeCookie("session", cookies.session);
      return navigate("/login");
    }

    setUser(data);
  }

  useEffect(() => {
    fetchUser();
  }, []);

  return <>{user?.name}</>;
}

export default Index;
