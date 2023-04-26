import { Component } from "react";
import './App.css';

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

    // restart bot if needed
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
                  <div className='status-container'>
                    <div>
                      <div className='status-item'>
                        <span className='status' id='status' status={status}>{status}</span>
                      </div>
                      <div className='relays-list'>
                        {Object.entries(settings.relays).map(([key, value]) => (
                          <div key={key} className="relay-item frosty">
                          <span className='connected-relay' id={key} {... (this.checkIfRelayIsConnected(value) ? {'data-connected': true} : {})}>{value}</span>
                          </div>
                        ))}
                      </div>
                      {status === 'RUNNING' ? (
                        <div>
                          <button className="button to_stop" onClick={() => this.stopBot(false)}>Stop bot</button>
                        </div>
                      ) : (
                        <div>
                          <button className="button to_start" onClick={() => this.startBot(false)}>Start bot</button>
                        </div>
                      )}
                    </div>
                  </div>
                ) : null}
                {settings ? (
                  <div>
                    <h2>Nostr Bot Settings</h2>
                    <div>
                      { editable ? (
                        <div>
                          <button className="button cancel-btn" onClick={this.cancelEditSettings}>Cancel</button>
                          <button className="button update-btn" onClick={this.updateSettings}>Save settings</button>
                        </div>
                      ) : (
                        <button className="button update-btn" onClick={this.editSettings}>Edit settings</button>
                      )}
                    </div>
                    <div className='settings'>
                    {Object.entries(settings).map(([key, value]) => (
                      <div className="settings-item frosty" key={key}>
                        <div className="label-container">
                          <label htmlFor={key}>{key}</label>
                        </div>
                        {Array.isArray(value) && editable ? (
                          <div className="input-list-container" key={`${key}-new`}>
                            <div className="input-list-content">
                              <input
                                className='settings-input-new'
                                id={`${key}-new`}
                                value={this.state[key + '-new'] || ''}
                                onChange={(e) => this.handleInputNewChange(e)}
                                placeholder="New item"
                              />
                            </div>
                            <div className="add-btn-content">
                              <button className='add-btn' onClick={() => this.addItem(key)}><i className="material-icons">add</i></button>
                            </div>
                          </div>
                        ) : null}
                        <div>
                          {Array.isArray(value) ? (
                            value.map((item, index) => (
                              <div className="input-list-container" key={`${key}-${index}`}>
                                <div className="input-list-content">
                                  <input
                                    className='settings-input-list'
                                    id={`${key}-${index}`}
                                    value={item}
                                    readOnly
                                    disabled
                                  />
                                </div>
                                {editable ? (
                                  <div className="remove-btn-content">
                                    <button className="remove-btn" onClick={() => this.removeItem(key, index)}><i className="material-icons">delete</i></button>
                                  </div>
                                ) : null}
                              </div>
                            ))
                          ) : (
                            <div className="input-list-container" key={key}>
                              <div className="input-list-content">
                                <input 
                                  className='settings-input' 
                                  id={key} 
                                  value={value}
                                  type={editable || this.state.secureInput[key]  ? 'text' : 'password'}
                                  onChange={(e) => this.handleInputChange(e, key)} 
                                  {... (editable ? {} : {readOnly: true, disabled: true})}
                                  />
                              </div>
                                {!editable ? (
                                  <div className="remove-btn-content">
                                    <button 
                                    className="secureToggleButton" 
                                    onClick={() => this.toggleSecureInput(key)}
                                    {... (!this.state.secureInput[key] ? {'data-secure': true} : {})}
                                  > 
                                    <span className="material-icons">{!this.state.secureInput[key] ? 'visibility' : 'visibility_off'}</span>
                                  </button>
                                </div>
                                ) : null}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  </div>
                ) : null }
              </div>
            )}
         </div>
      </div>
    );
  }
}

export default App;