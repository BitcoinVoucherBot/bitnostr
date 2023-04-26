import { Component } from "react";

class InputSingleComponent extends Component {

    render() {
        const { k, value, editable, handleInputChange, secureInput, toggleSecureInput } = this.props;
        return (
            <div className="input-list-container" key={k}>
                <div className="input-list-content">
                    <input 
                        className='settings-input' 
                        id={k} 
                        value={value}
                        type={editable || secureInput[k]  ? 'text' : 'password'}
                        onChange={(e) => handleInputChange(e, k)} 
                        {... (editable ? {} : {readOnly: true, disabled: true})}
                    />
                </div>
                {!editable ? (
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