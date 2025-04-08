export interface ApplicationDataT {
  application_id: string;
  client_id: string;
  application_name: string;
  scopes: string;
  bot_scopes: string;
  auths: number;
  allowed: string | null;
}

export interface UserDataT {
  id: number;
  twitch_id: number;
  name: string;
  token: string | null;
  applications: ApplicationDataT[];
}
