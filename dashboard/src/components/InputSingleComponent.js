import { Component } from "react";

class InputSingleComponent extends Component {


    isDefaultValue = (value) => {
        const regex = /<.*>/;
        if (regex.test(value)) {
            return true;
        }
        return false;
    }

    render() {
        const { k, value, editable, handleInputChange, secureInput, toggleSecureInput } = this.props;
        return (
            <div className="input-list-container" key={k}>
                <div className="input-list-content">
                    <input 
                        className='settings-input' 
                        id={k} 
                        value={value}
                        type={editable || secureInput[k] || this.isDefaultValue(value)  ? 'text' : 'password'}
                        onChange={(e) => handleInputChange(e, k)} 
                        {... (editable ? {} : {readOnly: true, disabled: true})}
                    />
                </div>
                {!editable && !this.isDefaultValue(value) ? (
                    <div className="remove-btn-content">
                    <button 
                        className="secureToggleButton" 
                        onClick={() => toggleSecureInput(k)}
                        {... (!secureInput[k] ? {'data-secure': true} : {})}
                        > 
                        <span className="material-icons">{!secureInput[k] ? 'visibility' : 'visibility_off'}</span>
                    </button>
                </div>
                ) : null}
            </div>
        )
    }
}

export default InputSingleComponent;