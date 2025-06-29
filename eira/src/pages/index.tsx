import { useEffect, useRef, useState } from "react";
import type { UserDataT } from "../types/responses";
import { useLocation } from "wouter";
import "./css/index.css";
import { useCookies } from "react-cookie";

function Index() {
  const [user, setUser] = useState<UserDataT>();
  const [token, setToken] = useState<string | null>(null);
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
    const host = `${window.location.protocol}//${window.location.host}`;
    const apps = user?.applications.map((app) => {
      return (
        <div key={app.application_id}>
          <div className="appDetails">
            <h2 className="lightPurple">{app.application_name}</h2>
            <span>
              <b>Application-ID</b>
              <span className="highlight">{app.application_id}</span>
            </span>
            <span>
              <b>Twitch Client-ID</b>
              <span className="highlight">{app.client_id}</span>
            </span>
            <span>
              <b>Auth URL</b>
              <span className="highlight">{`${host}/oauth/${app.url}`}</span>
            </span>
            <span>
              <b>Redirect URL</b>
              <span className="highlight">{`${host}/oauth/redirect/${app.url}`}</span>
            </span>
            <button type="button" className="simpleButton redButton" onClick={deleteApp}>
              Delete
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

  const deleteApp = async () => {
    let resp: Response;

    if (!user?.applications) {
      return;
    }

    const data = {
      application_id: user.applications[0].application_id,
    };

    try {
      resp = await fetch("/users/apps", { method: "DELETE", credentials: "include", body: JSON.stringify(data) });
    } catch (error) {
      setError(`Unable to delete app: ${error}`);
      return;
    }

    if (!resp.ok) {
      const body = await resp.text();
      setError(`Unable to delete app: ${body} (${resp.status})`);
      return;
    }

    await fetchUser();
  };

  const getToken = async () => {
    let resp: Response;

    if (!cookies.session) {
      return navigate("/login");
    }

    try {
      resp = await fetch("/users/token", { credentials: "include" });
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

    setToken(data.token);
  };

  const getStatus = () => {
    if (!user) {
      return "No Application";
    }

    if (user.applications.length === 0) {
      return "No Application";
    }

    const app = user.applications[0];
    const status = user.status ? <b className="green">Connected</b> : <b className="warningRed">Not Connected</b>;
    return (
      <div className="status">
        <b style={{ fontSize: "1.1em" }}>{app.application_name}</b>
        {status}
      </div>
    );
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
          <a href="/users/logout" type="button" className="simpleButton">
              Logout
          </a>

          <div className="innerDetails">
            <b className="lightPurple">API Token</b>
            <span>Your access token to TwitchIO Token Relay.</span>
            <span>To view this token you must generate a new one. You must keep this token confidential.</span>
            <button type="button" className="simpleButton" onClick={getToken}>
              Generate Token
            </button>
            {token ? (
              <div className="appDetails">
                <span>
                  <b>API Token</b>
                  <span className="highlight">{token}</span>
                </span>
              </div>
            ) : null}
          </div>
        </div>

        <div className="details">
          <h3>Applications</h3>
          <hr className="hrW" />
          <span>
            Currently the <b>TwitchIO Token Relay</b> service only allows one application per user.
          </span>
          <span>
            After creating your app, select scopes by visiting the <a href="https://chillymosh.com/tools/twitch-scopes/" target="_blank">Scope Selector</a>. 
            Select the <b>Custom URL</b> option and paste in the <b>Auth URL</b> from below.<br/>
            You should add the <b>Redirect URL</b> below to your application on the <a href="https://dev.twitch.tv/console">Twitch Developer Console</a>.
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
                <b>Twitch Client-ID:</b>
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
          <div>{user ? getStatus() : null}</div>
          <hr className="hrW" />
        </div>
      </main>
    </>
  );
}

export default Index;
