import { Component } from "react";

class InputListComponent extends Component {

    render() {
        const { k, index, item, editable, removeItem } = this.props;
        return (
            <div className="input-list-container" key={`${k}-${index}`}>
                <div className="input-list-content">
                    <input
                    className='settings-input-list'
                    id={`${k}-${index}`}
                    value={item}
                    readOnly
                    disabled
                    />
                </div>
                {editable ? (
                    <div className="remove-btn-content">
                        <button className="remove-btn" onClick={() => removeItem(k, index)}><i className="material-icons">delete</i></button>
                    </div>
                ) : null}
            </div>
        )
    }
}

export default InputListComponent;