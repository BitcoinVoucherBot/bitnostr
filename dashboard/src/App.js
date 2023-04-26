import { Component } from "react";
import './App.css';
import StatusComponent from './components/StatusComponent';
import SettingsComponent from './components/SettingsComponent';

class App extends Component {
  
  constructor(props) {
    super(props);
    this.state = {
      settings: null,
      status: 'RUNNING',
      connected: [],
      editable: false,
      secureInput: {},
      loading: true
    };

    setTimeout(() => {
      this.fetchData();
    }, 3000);
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
      const response = await fetch('http://localhost:8080/bot/settings');
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
      
      this.setData(settingsJson);
    } catch (error) {
      console.error(`Error fetching settings: ${error.message}`);
    }
  }

  async fetchInfo() {
    try {
      const response = await fetch('http://localhost:8080/info');
      if (!response.ok) {
        throw new Error(`Fetch failed with status ${response.status}`)
      }
      const jsonResponse = await response.json();
      const info = jsonResponse.info
      this.setState({
        status: info.status,
        connected: info.connected
      })
    } catch (error) {
      console.error(`Error fetching info: ${error.message}`);
    }
  }

  setData(params) {
    this.setState({ settings: params });
  }

  updateSettings = async () => {
    let confirm = window.confirm('Are you sure you want to update the settings?\nIn order to apply the changes, the bot will be restarted.');
    if (!confirm) {
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
    const response = await fetch('http://localhost:8080/bot/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    });
    const jsonResponse = await response.json();
    console.log(jsonResponse);

    this.setState({ status: 'RESTARTING', connected: [] });
    setTimeout(() => {
      this.stopBot(true);
      setTimeout(() => {
        this.startBot(true);
        this.setState({ editable: false });
      }, 5000);
    }, 5000);
  }

  editSettings = () => {
    this.setState({ editable: true });
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

  startBot = async (force) => {
    if (!force) {
      let confirm = window.confirm('Are you sure you want to start the bot?');
      if (!confirm) {
        return;
      }
    }
    const response = await fetch('http://localhost:8080/bot/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
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

  stopBot = async (force) => {
    if (!force) {
      let confirm = window.confirm('Are you sure you want to force stop the bot?');
      if (!confirm) {
        return;
      }
    }
    const response = await fetch('http://localhost:8080/bot/stop', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
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

  render() {
    const { settings, status, editable, loading } = this.state;
    return (
      <div className="container">
         <div className="background-image"></div>
         <div className="content">
          <div className="header">
            <img className="header-logo" src="logo.png" />
            <h1 className="header-title">BitcoinVoucherBot</h1>
          </div>
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
                    secureInput={this.state.secureInput}
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
      </div>
    );
  }
}

export default App;