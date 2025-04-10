import { useEffect, useRef, useState } from "react";
import type { UserDataT } from "../types/responses";
import { useLocation } from "wouter";
import "./css/index.css";
import { useCookies } from "react-cookie";

function Index() {
  const [user, setUser] = useState<UserDataT>();
  const [, navigate] = useLocation();
  const [cookies, , removeCookie] = useCookies(["session"]);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const cidRef = useRef<HTMLInputElement>(null);
  const nameRef = useRef<HTMLInputElement>(null);

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

  const getApps = () => {
    const apps = user?.applications.map((app) => {
      return (
        <div key={app.application_id}>
          <div className="appDetails">
            <b className="lightPurple">{app.application_name}</b>
            <span>{app.client_id}</span>
            <button type="button" className="simpleButton">
              Edit
            </button>
          </div>
          <hr className="hrW" />
        </div>
      );
    });

    if (!apps || (apps.length === 0 && !showForm)) {
      return (
        <button type="button" className="simpleButton" onClick={() => setShowForm(true)}>
          + Create New
        </button>
      );
    }

    return apps;
  };

  const saveNewApp = async () => {
    let resp: Response;

    if (!cookies.session) {
      return navigate("/login");
    }

    if (!cidRef.current || !nameRef.current) {
      setError("Error: Reload and try again");
      return;
    }

    const name = nameRef.current.value;
    const clientId = cidRef.current.value;

    if (!name) {
      setError("Please enter a valid application name");
      return;
    }

    if (!clientId) {
      setError("Please enter a valid Client-ID");
      return;
    }

    const data = {
      name: name,
      client_id: clientId,
    };

    try {
      resp = await fetch("/users/apps", { credentials: "include", method: "POST", body: JSON.stringify(data) });
    } catch (error) {
      setError("An unexpected error occurred. Please try again later.");
      return;
    }

    if (!resp.ok) {
      const msg = await resp.text();
      setError(msg);
      return;
    }

    const respData: UserDataT = await resp.json();

    setShowForm(false);
    setUser(respData);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <>
      <main>
        <h1 className="lightPurple">TwitchIO Token Relay</h1>
        <hr />
        <div className="details">
          <div className="innerDetails">
            <b className="lightPurple">Account ID</b>
            {user?.id}
          </div>
          <div className="innerDetails">
            <b className="lightPurple">Twitch</b>
            {user?.name} | {user?.twitch_id}
          </div>

          <div className="innerDetails">
            <b className="lightPurple">API Token</b>
            <span>Your access token to TwitchIO Token Relay.</span>
            <span>To view this token you must generate a new one. You must keep this token confidential.</span>
            <button type="button" className="simpleButton">
              Generate Token
            </button>
          </div>
        </div>

        <div className="details">
          <h3>Applications</h3>
          <hr className="hrW" />
          <span>
            Currently the <b>TwitchIO Token Relay</b> service only allows one application per user.
          </span>
          {getApps()}
          {showForm ? (
            <div className="appForm">
              <span>
                Please complete the form below to create a new application. The name and Client-ID should match the
                application you created on the <a href="https://dev.twitch.tv/console">Twitch Developer Console.</a>
              </span>
              <span className="lightPurple">
                <b>Name:</b>
              </span>
              <input type="text" ref={nameRef} />
              <span className="lightPurple">
                <b>Client-ID:</b>
              </span>
              <input type="text" ref={cidRef} />
              {error ? <span className="warningRed">{error}</span> : null}
              <button type="button" className="simpleButton" onClick={saveNewApp}>
                Save
              </button>
            </div>
          ) : null}
        </div>

        <div className="details">
          <h3>Status</h3>
          <hr className="hrW" />
        </div>
      </main>
    </>
  );
}

export default Index;
