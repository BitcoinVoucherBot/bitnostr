import { Component } from "react";
import './App.css';

class App extends Component {
  
  constructor(props) {
    super(props);
    this.state = {
      settings: null,
      status: 'RUNNING',
      connected: []
    };
  }

  componentDidMount() {
    this.fetchSettings();
    this.fetchInfo();

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
    let confirm = window.confirm('Are you sure you want to update the settings?');
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
  }

  addItem = (key) => {
    const newValue = this.state[key + '-new'] || '';
    if (newValue !== '' && !this.state.settings[key].includes(newValue)) {
      this.setState(prevState => {
        const values = [...prevState.settings[key], newValue];
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

  handleChange = (e) => {
    this.setState({ [e.target.id]: e.target.value });
  }

  startBot = async () => {
    let confirm = window.confirm('Are you sure you want to start the bot?');
    if (!confirm) {
      return;
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
      const status = jsonResponse.status;
      this.setState({ status: status });
    } else {
      alert(response.statusText);
      this.setState({ status: "STOPPED" });
    }
  }

  stopBot = async () => {
    let confirm = window.confirm('Are you sure you want to stop the bot?');
    if (!confirm) {
      return;
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
      this.setState({ status: status });
    } else {
      alert(response.statusText);
      this.setState({ status: "STOPPED" });
    }
  }

  render() {
    const { settings, status, connected } = this.state;
    return (
      <div>
        <h1>BitcoinVoucherBot - Nostr</h1>
        <h2>Info</h2>
        { status && connected ? (
          <div className='status'>
            <div className='status-item'>
              <label htmlFor='status'>Status</label>
              <input className='status-input' id='status' value={status} readOnly />
            </div>
            <div className='status-item'>
              <label htmlFor='connected'>Connected Relays</label>
              {Object.entries(connected).map(([key, value]) => (
                <div key={key}>
                  <input className='status-input' id={key} value={value} readOnly />
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p>Loading...</p>
        )}
        <h2>Settings</h2>
        {settings ? (
          <div className='settings'>
            {Object.entries(settings).map(([key, value]) => (
              <div key={key}>
                <label htmlFor={key}>{key}</label>
                {Array.isArray(value) ? (
                  value.map((item, index) => (
                    <div key={`${key}-${index}`}>
                      <input
                        className='settings-input-list'
                        id={`${key}-${index}`}
                        value={item}
                        readOnly
                      />
                      <button onClick={() => this.removeItem(key, index)}>Remove</button>
                    </div>
                  ))
                ) : (
                  <div key={key}>
                    <input className='settings-input' id={key} value={value} readOnly />
                  </div>
                )}
                {Array.isArray(value) ? (
                  <div key={`${key}-new`}>
                    <input
                      className='settings-input-new'
                      id={`${key}-new`}
                      value={this.state[key + '-new'] || ''}
                      onChange={this.handleChange}
                    />
                    <button onClick={() => this.addItem(key)}>Add</button>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        ) : (
          <p>Loading...</p>
        )}
        <div>
          <button onClick={this.updateSettings}>Update settings</button>
        </div>
        {status === 'RUNNING' ? (
          <div>
            <button onClick={this.stopBot}>Stop bot</button>
          </div>
        ) : (
          <div>
            <button onClick={this.startBot}>Start bot</button>
          </div>
        )}
      </div>
    );
  }
}

export default App;