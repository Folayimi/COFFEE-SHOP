
export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'rinfix.us.auth0.com', // the auth0 domain prefix
    audience: 'drinkmenu', // the audience set for the auth0 app
    clientId: 'PBv9Ry1aM3Ssiq2t0qsAOVZTdY7q0piG', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:8080/login-results', // the base url of the running ionic application. 
  }
};
