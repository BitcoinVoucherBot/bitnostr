import { Component } from "react";
import InputListNew from './InputListNew';
import InputListComponent from './InputListComponent';
import InputSingleComponent from './InputSingleComponent';

class SettingsComponent extends Component {

    sanitize (value) {
        return value.replace(/_/g, ' ').toUpperCase();
    }

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
                                <label htmlFor={key}>{this.sanitize(key)}</label>
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
                                    // check if value is empty array
                                    value.length > 0 ? (
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
                                        <div className="empty-list">
                                            <p>Empty list</p>
                                            <p>Add at least one item to the list</p>
                                        </div>
                                    )   
                                ) : (
                                    <InputSingleComponent 
                                        k={key}
                                        value={value}
                                        editable={editable}
                                        handleInputChange={(e) => handleInputChange(e, key)}
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