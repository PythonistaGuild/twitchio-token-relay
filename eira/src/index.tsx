/* @refresh reload */
import { render } from "solid-js/web";
import { Router, Route } from "@solidjs/router";
import "./index.css";
import HomePage from "./pages/Home";
import DashboardPage from "./pages/Dashboard";

const root = document.getElementById("root");

render(
	() => (
		<Router>
			<Route path="/dashboard/landing" component={HomePage} />
			<Route path="/dashboard" component={DashboardPage} />
		</Router>
	),
	root!,
);
