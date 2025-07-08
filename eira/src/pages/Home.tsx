import "./css/Home.css";
import TwitchLogo from "../assets/twitch-logo.svg";
import Carousel from "../components/Slider";


function HomePage() {
	return (
		<>
			<main>
				<div class="left">
					<h1>TwitchIO <span class="blue">OAuth Relay</span></h1>
					<p>Easily and securely re-route OAuth to your Twitch applications</p>
					<Carousel>
						<div class="embla__slide">
							The <b>TwitchIO OAuth Relay</b> is a free service, providing an easy and secure way to relay OAuth requests from Twitch to your application over websockets. No domain or Static IP address required.
						</div>
						<div class="embla__slide">
							<b>Create</b> an application. <b>Connect</b> via Secure-Websocket. <b>Receive</b> and complete OAuth flows locally with your application without sharing any secrets, tokens or sensitive data.
						</div>
						<div class="embla__slide">
							TwitchIO OAuth Relay has no access to the authenticated user's data; you complete the OAuth flow locally without ever exposing your secret. We simply relay the code needed for your Client-ID/Secret to complete the OAuth request.
						</div>
					</Carousel>
					<div class="socials">
						<a href="/">GitHub</a>
						<a href="/">Documentation</a>
						<a href="/">Conditions</a>
					</div>
				</div>
				<div class="right">
					<h2>Dashboard</h2>
					<a class="loginButton button" href="/login" >
						<img src={TwitchLogo}></img>
						Sign in via Twitch
					</a>
				</div>
			</main>
		</>
	);
}

export default HomePage;
