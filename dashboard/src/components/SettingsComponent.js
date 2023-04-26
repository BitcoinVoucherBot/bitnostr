import { Component } from "react";
import InputListNew from './InputListNew';
import InputListComponent from './InputListComponent';
import InputSingleComponent from './InputSingleComponent';

class SettingsComponent extends Component {

    render() {
        const { 
            state, 
            settings, 
            editable, 
            secureInput, 
            cancelEditSettings, 
            updateSettings, 
            editSettings, 
            removeItem, 
            handleInputChange, 
            toggleSecureInput,
            handleInputNewChange,
            addItem, 
        } = this.props;
        return (
            <div>
                <h2>Nostr Bot Settings</h2>
                <div>
                    { editable ? (
                    <div>
                        <button className="button cancel-btn" onClick={cancelEditSettings}>Cancel</button>
                        <button className="button update-btn" onClick={updateSettings}>Save settings</button>
                    </div>
                    ) : (
                    <button className="button update-btn" onClick={editSettings}>Edit settings</button>
                    )}
                </div>
                <div className='settings'>
                    {Object.entries(settings).map(([key, value]) => (
                        <div className="settings-item frosty" key={key}>
                            <div className="label-container">
                                <label htmlFor={key}>{key}</label>
                            </div>
                            {Array.isArray(value) && editable ? (
                                <InputListNew 
                                    k={key}
                                    state={state}
                                    handleInputNewChange={(e) => handleInputNewChange(e)}
                                    addItem={(key) => addItem(key)}
                                />
                            ) : null}
                            <div>
                                {Array.isArray(value) ? (
                                    value.map((item, index) => (
                                        <InputListComponent 
                                            key={`${key}-${index}`}
                                            k={key}
                                            index={index}
                                            item={item}
                                            editable={editable}
                                            removeItem={(k, index) => removeItem(k, index)}
                                        />
                                    ))
                                ) : (
                                    <InputSingleComponent 
                                        k={key}
                                        value={value}
                                        editable={editable}
                                        handleInputChange={(e) => handleInputChange(e)}
                                        secureInput={secureInput}
                                        toggleSecureInput={(e) => toggleSecureInput(e)}
                                    />
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )
    }
}

export default SettingsComponent;