import { Route, Switch } from "wouter";
import Index from "./pages";
import LoginPage from "./pages/login";
import { CookiesProvider } from "react-cookie";

function App() {
  return (
    <>
      <CookiesProvider>
        <Switch>
          <Route path="/" component={Index} />
          <Route path="/login" component={LoginPage} />
        </Switch>
      </CookiesProvider>
    </>
  );
}

export default App;
