import { useEffect } from "react";
import type { UserDataT } from "../types/responses";
import { useLocation } from "wouter";
import { useCookies } from "react-cookie";
import "./css/login.css";
import TwitchLogo from "../assets/twitch.svg";

function LoginPage() {
  const [, navigate] = useLocation();
  const [cookies, , removeCookie] = useCookies(["session"]);

  async function fetchUser() {
    let resp: Response;

    if (!cookies.session) {
      return;
    }

    try {
      resp = await fetch("/users/@me", { credentials: "include" });
    } catch (error) {
      console.error(error);
      return;
    }

    if (!resp.ok) {
      throw new Error(`Unable to fetch user data from API: ${resp.status}`);
    }

    const data: UserDataT = await resp.json();
    if (!data) {
      removeCookie("session", cookies.session);
      return;
    }

    return navigate("/");
  }

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <>
      <div className="loginLeft">
        <h1>TwitchIO Token Relay</h1>
        <hr />

        <div className="infoSec">
          <p>
            The TwitchIO Token Relay is a service provided to relay OAuth requests from Twitch to your Twitch
            Application. We do this by providing a public URL that you, or anyone else wanting to use your application,
            can visit to directly authorize your Twitch Application with the appropriate scopes. The exchange occurs
            over websockets, so you don't need a public domain or exposed IP with open ports.
            <br />
            <br />
            We <b className="warningRed">DO NOT</b> store or ask for tokens or secrets or any other secret information relating to your
            Twitch application.
            <br />
            <br />
            We <b className="warningRed">DO</b> store your Twitch User ID and Twitch Application Client-ID.
            <br />
            <br />
            You can view the source for this service on{" "}
            <a href="https://github.com/PythonistaGuild/twitchio-token-relay">GitHub</a>
            <br />
            <br />
            We are <b className="warningRed">NOT</b> and this service is <b className="warningRed">NOT</b> affiliated
            with Twitch.
          </p>

          <h3>Who is this for?</h3>
          <p>
            <ul>
              <li>Anyone without a Public Domain</li>
              <b>AND</b>
              <li>Anyone without a Static IP (Or anyone not willing to expose it).</li>
              <b>OR</b>
              <li>Anyone not able to open a public port on their IP.</li>
              <b>AND</b>
              <li>Anyone who wants to authorize multiple users.</li>
            </ul>
          </p>

          <h3 className="warningRed">Who is this NOT for?</h3>
          <p>
            <ul>
              <li>Anyone with a Public Domain</li>
              <b>OR</b>
              <li>Anyone who is willing to expose and use a Static IP Address with an open port</li>
              <b>OR</b>
              <li>Anyone only Authorizing themselves or their own Applications (Not other users)</li>
            </ul>
          </p>
        </div>
        <h1>How it works</h1>
        <hr />
        <p>
          After you login and create an application on your dashboard you will be provided with two URLs.<br/><br/>

          When a user visits the provided <b>Auth URL</b> with your chosen scopes, they are redirected to authenticate on Twitch as standard.<br/>
          When a user successfully authenticates your application Twitch sends us a "code" as part of the OAuth flow. This code is sent to
          your bot securely via authenticated websocket for you to complete the flow: The token relay has no access the the authenticated user's data.<br/><br/>

          <b className="warningRed">NEVER</b> send anyone your Client-Secret, including to this or anyone claiming to be this website!
        </p>

      </div>

      <div className="loginRight">
        <div className="loginInfo">
          <h1>Login</h1>
          <span>
            To access the <b>TwitchIO Token Relay</b> please login via Twitch.
          </span>
          <span>
            Please use the account you manage your Twitch Applications with on the{" "}
            <a href="https://dev.twitch.tv/console">Twitch Developer Console</a>
          </span>

          <a className="loginButton" href="/users/login">
            <img src={TwitchLogo} alt="Twitch Logo" />
            Sign in with Twitch
          </a>
        </div>
      </div>
    </>
  );
}

export default LoginPage;
