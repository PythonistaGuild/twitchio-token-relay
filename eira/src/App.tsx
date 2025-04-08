import { Route, Switch } from "wouter";
import Index from "./pages";
import LoginPage from "./pages/login";


function App() {
  return (
    <>
        <Switch>
          <Route path="/" component={Index}/>
          <Route path="/login" component={LoginPage} />
        </Switch>
    </>
  );
}

export default App;
