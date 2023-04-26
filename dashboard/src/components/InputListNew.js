import React, { Component } from 'react';

class InputListNew extends Component {

  handleInputNewChange(e) {
    this.props.handleInputNewChange(e, this.props.key);
  }

  render() {
    const { k, addItem, state } = this.props;
    return (
      <div className="input-list-container" key={`${k}-new`}>
        <div className="input-list-content">
          <input
            className='settings-input-new'
            id={`${k}-new`}
            value={state[k + '-new'] || ''}
            onChange={(e) => this.handleInputNewChange(e)}
            placeholder="New item"
          />
        </div>
        <div className="add-btn-content">
          <button className='add-btn' onClick={() => addItem(k)}><i className="material-icons">add</i></button>
        </div>
      </div>
    );
  }
}

export default InputListNew;