import { Route, Switch } from "wouter";
import Index from "./pages";


function App() {
  return (
    <>
        <Switch>
          <Route path="/" component={Index}/>
        </Switch>
    </>
  );
}

export default App;
