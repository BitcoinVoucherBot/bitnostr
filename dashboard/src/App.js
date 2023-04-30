import { Component } from "react";
import './App.css';
import StatusComponent from './components/StatusComponent';
import SettingsComponent from './components/SettingsComponent';
import LoginComponent from "./components/LoginComponent";

class App extends Component {
  
  constructor(props) {
    super(props);
    this.state = {
      base_url: '',
      settings: null,
      status: 'RUNNING',
      connected: [],
      editable: false,
      secureInput: {},
      loading: true,
      isLogged: false,
    };

    setTimeout(() => {
      this.fetchData();
    }, 3000);

    this.fetchData = this.verifyLogin(this.fetchData);
    this.fetchSettings = this.verifyLogin(this.fetchSettings);
    this.fetchInfo = this.verifyLogin(this.fetchInfo);
    this.updateSettings = this.verifyLogin(this.updateSettings);
    this.startBot = this.verifyLogin(this.startBot);
    this.stopBot = this.verifyLogin(this.stopBot);
  }

  componentDidMount() {
    let base_url = window.location.href.replace(':3000', '');
    if (base_url[base_url.length - 1] === '/') {
      base_url = base_url.slice(0, -1);
    }
    this.setState({ base_url: base_url })
    const token = this.getToken();
    if (token) {
      this.setState({ isLogged: true }, () => {
        this.fetchData();
      });
    }
  }

  verifyLogin = (method) => {
    return function (...args) {
      if (this.state.isLogged) {
        return method.apply(this, args)
      } else {
        // Handle the case when the user is not logged in
        console.log('User is not logged in. Cannot execute method.');
        this.setState({ loading: false });
      }
    }
  }

  async login(username, password) {
    const token = btoa(`${username}:${password}`);
    try {
      const response = await fetch(this.state.base_url + ':8080/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      if (response.status !== 200) {
        this.setState({ isLogged: false });  
        alert('Wrong username or password')
      } else {
        this.setToken(token);
        this.setState({ isLogged: true }, () => {
          this.fetchData();
        });
      }
    } catch (error) {
      alert(`Error logging in: ${error.message}`)
    }
  }

  logout = () => {
    let confirm = window.confirm('Are you sure you want to logout?');
    if (!confirm) return;
    this.setState({ isLogged: false });
    localStorage.removeItem('token');
  }

  setToken = (token) => {
    localStorage.setItem('token', token);
  }

  getToken = () => {
    const token = localStorage.getItem('token');
    if (token) {
      return token
    }
    return null;
  }  

  fetchData() {
    this.fetchSettings();
    this.fetchInfo();

    this.setState({ loading: false });

    setInterval(() => {
      this.fetchInfo();
    }, 30 * 1000);
  }

  async fetchSettings() {
    try {
      const token = this.getToken();
      if (token) {
        const headers = new Headers();
        headers.append('Authorization', `Basic ${token}`);
        const response = await fetch(this.state.base_url + ':8080/bot/settings', { headers });

        if (!response.ok) {
          throw new Error(`Fetch failed with status ${response.status}`)
        }
        const jsonResponse = await response.json();
        const settings = jsonResponse.settings
        const settingsJson = JSON.parse(settings)
        // Remove unnecessary data
        delete settingsJson['enabled'];
        delete settingsJson['last_message_created_at'];
        delete settingsJson['lightning_tiers'];
        delete settingsJson['on_chain_tiers'];
        delete settingsJson['nip05_verification'];
        delete settingsJson['message_to_sign'];
  
        // check if settingsJson.admin contain <ADMIN_ID> and remove it from list
        if (settingsJson.admins.includes('<ADMIN_ID>')) {
          settingsJson.admins = settingsJson.admins.filter((id) => id !== '<ADMIN_ID>');
        }
        
        this.setData(settingsJson);
      } else {
        console.log('No token found. Cannot fetch settings.');
      }
    } catch (error) {
      console.error(`Error fetching settings: ${error.message}`);
    }
  }

  async fetchInfo() {
    try {
      const token = this.getToken();
      if (token) {
        const headers = new Headers();
        headers.append('Authorization', `Basic ${token}`);
        const response = await fetch(this.state.base_url + ':8080/info', { headers });

        if (!response.ok) {
          throw new Error(`Fetch failed with status ${response.status}`)
        }
        const jsonResponse = await response.json();
        const info = jsonResponse.info
        this.setState({
          status: info.status,
          connected: info.connected
        })
      } else {
        console.log('No token found. Cannot fetch info.');
      }
    } catch (error) {
      console.error(`Error fetching info: ${error.message}`);
    }
  }

  setData(params) {
    this.setState({ settings: params });
  }

  async updateSettings() {
    let confirm = window.confirm('Are you sure you want to update the settings?\nIn order to apply the changes, the bot will be manually restarted.');
    if (!confirm) {
      return;
    }

    const token = this.getToken();
    if (!token) {
      console.log('No token found. Cannot update settings.');
      return;
    }

    const settings = {};
    const inputs = document.querySelectorAll('.settings-input');
    // only text inputs
    inputs.forEach((input) => {
      settings[input.id] = input.value;
    })
    const inputsList = document.querySelectorAll('.settings-input-list');
    inputsList.forEach((input) => {
      const key = input.id.split('-')[0]
      if (!settings[key]) {
        settings[key] = []
      }
      settings[key].push(input.value)
    })
    const response = await fetch(this.state.base_url + ':8080/bot/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${token}`
      },
      body: JSON.stringify(settings)
    });
    const jsonResponse = await response.json();
    console.log(jsonResponse);

    this.setState({ editable: false });
  }

  editSettings = () => {
    if (this.state.status !== 'RUNNING') {
      this.setState({ editable: true });
    } else {
      alert('Please stop the bot before editing the settings.\nThan restart it after you are done.');
    }
  }

  cancelEditSettings = () => {
    let confirm = window.confirm('Are you sure you want to cancel editing?');
    if (!confirm) {
      return;
    }

    this.setState({ editable: false });
    this.fetchSettings();
  }

  addItem = (key) => {
    const newValue = this.state[key + '-new'] || '';
    if (newValue !== '' && !this.state.settings[key].includes(newValue)) {
      this.setState(prevState => {
        const values = [newValue, ...prevState.settings[key]];
        const new_obj = { ...prevState.settings, [key]: values };
        return { settings: new_obj, [key + '-new']: '' };
      });
    } else {
      alert('Please enter a value and make sure it is not already in the list');
    }
  }

  removeItem = (key, index) => {
    this.setState(prevState => {
      const values = prevState.settings[key].filter((_, i) => i !== index);
      const new_obj = { ...prevState.settings, [key]: values };
      return { settings: new_obj };
    });
  }

  handleInputNewChange = (e) => {
    this.setState({ [e.target.id]: e.target.value });
  }

  handleInputChange = (e, key, index=0) => {
    const { value } = e.target;
    this.setState(prevState => {
      prevState.settings[key] = value
      return { settings: prevState.settings };
    });
  }

  toggleSecureInput = (inputId) => {
    this.setState(prevState => ({
      secureInput: {
        ...prevState.secureInput,
        [inputId]: !prevState.secureInput[inputId]
      }
    }));
  }

  checkIfSettingsAreValid = () => {
    let nostr_private_key_valid = false
    let nostr_public_key_valid = false
    let bvb_api_key_valid = false
    let bot_api_key_valid = false
    let relays_valid = false
    let admins_valid = false
    const settings = this.state.settings;
    if (settings.nostr_private_key !== '' && settings.nostr_private_key !== '<NOSTR_PRIVATE_KEY>') {
      nostr_private_key_valid = true
    }
    if (settings.nostr_public_key !== '' && settings.nostr_public_key !== '<NOSTR_PUBLIC_KEY>') {
      nostr_public_key_valid = true
    }
    if (settings.bvb_api_key !== '' && settings.bvb_api_key !== '<BVB_API_KEY>') {
      bvb_api_key_valid = true
    }
    if (settings.bot_api_key !== '' && settings.bot_api_key !== '<BOT_API_KEY>') {
      bot_api_key_valid = true
    }
    if (settings.relays.length > 0) {
      relays_valid = true
    }
    if (settings.admins.length > 0 && !settings.admins.includes('<ADMIN_ID>')) {
      admins_valid = true
    }

    return nostr_private_key_valid && nostr_public_key_valid && bvb_api_key_valid && bot_api_key_valid && relays_valid && admins_valid
  }

  async startBot(force) {
    if (!force) {
      let confirm = window.confirm('Are you sure you want to start the bot?');
      if (!confirm) {
        return;
      }
    }

    const token = this.getToken();
    if (!token) {
      console.log('No token found. Cannot start bot.');
      return;
    }

    if (!this.checkIfSettingsAreValid()) {
      alert('Please make sure all the settings are valid before starting the bot.');
      return;
    }

    const response = await fetch(this.state.base_url + ':8080/bot/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${token}`
      },
      body: JSON.stringify({ '': '' })
    });
    const jsonResponse = await response.json();
    if (response.status == 200) {
      if (jsonResponse.success == false) {
        alert(jsonResponse.message);
      }
      const status = jsonResponse.status;
      this.setState({ status: status }); 
      this.fetchInfo(); 
    } else {
      alert(response.statusText);
      this.setState({ status: "STOPPED", connected: [] });
    }
  }

  async stopBot(force) {
    if (!force) {
      let confirm = window.confirm('Are you sure you want to force stop the bot?');
      if (!confirm) {
        return;
      }
    }

    const token = this.getToken();
    if (!token) {
      console.log('No token found. Cannot stop bot.');
      return;
    }

    const response = await fetch(this.state.base_url + ':8080/bot/stop', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${token}`
      },
      body: JSON.stringify({ '': '' })
    });
    const jsonResponse = await response.json();
    console.log(jsonResponse);
    if (response.status == 200) {
      const status = jsonResponse.status;
      this.setState({ status: status, connected: [] });
    } else {
      alert(response.statusText);
      this.setState({ status: "STOPPED", connected: [] });
    }
  }

  checkIfRelayIsConnected = (relay) => {
    const relays = this.state.connected;
    if (relays.includes(relay)) {
      return true;
    }
    return false;
  }

  handleLoginSubmit = (props) => {
    const { username, password } = props;
    this.login(username, password);
  }

  render() {
    const { settings, status, editable, loading, secureInput, isLogged } = this.state;
    return (
      <div className="container">
         <div className="background-image"></div>
         <div className="content">
          <div className="header">
            <img className="header-logo" src="logo.png" />
            <h1 className="header-title">BitcoinVoucherBot</h1>
            { isLogged ? (
              <div className="logout-button" onClick={() => this.logout()} />
            ) : null}  
          </div>
          { !isLogged ? (
            <LoginComponent 
              handleLoginSubmit={(e) => this.handleLoginSubmit(e)}
            />
          ) : (
            <div>
              { loading ? (
                <div className="loader-container">
                  <div className="loader"/>
                </div>
                ) : (
                  <div>
                    { settings && status && settings.relays ? (
                      <StatusComponent 
                        status={status}
                        settings={settings}
                        checkIfRelayIsConnected={(e) => this.checkIfRelayIsConnected(e)}
                        startBot={() => this.startBot(false)}
                        stopBot={() => this.stopBot(false)}
                      />
                    ) : null}
                    {settings ? (
                      <SettingsComponent 
                        state={this.state}
                        settings={settings}
                        editable={editable}
                        secureInput={secureInput}
                        cancelEditSettings={() => this.cancelEditSettings()}
                        updateSettings={() => this.updateSettings()}
                        editSettings={() => this.editSettings()}
                        removeItem={(key, index) => this.removeItem(key, index)}
                        handleInputChange={(e, key, index) => this.handleInputChange(e, key, index)}
                        toggleSecureInput={(inputId) => this.toggleSecureInput(inputId)}
                        handleInputNewChange={(e) => this.handleInputNewChange(e)}
                        addItem={(key) => this.addItem(key)}
                      />
                    ) : null }
                  </div>
                )}
            </div>
          )}

          

         </div>
      </div>
    );
  }
}

export default App;