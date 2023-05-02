import React, { Component } from "react";
import InputSingleComponent from "./InputSingleComponent";

class LoginComponent extends Component {

    handleUsernameChange = (e) => {
        this.props.handleUsernameChange(e.target.value);
    };

    handlePasswordChange = (e) => {
        this.props.handlePasswordChange(e.target.value);
    };

    handleLoginSubmit = (e) => {
        this.props.handleLoginSubmit(e);
    };

    onSubmit = (e) => {
        e.preventDefault();
    };

    render() {
        const { k, username, password, secureInput, toggleSecureInput } = this.props
        return (
            <div className="login-container frosty">
                <form onSubmit={(e) => this.onSubmit(e)}>
                    <div className="label-container">
                        <label>Username:</label>
                    </div>
                    <input 
                        type="text" 
                        value={username}
                        placeholder="Type your username" 
                        onChange={(e) => this.handleUsernameChange(e)} 
                    />
                    <div className="label-container">
                        <label>Password:</label>
                    </div>
                    <div className="input-list-container">
                        <div className="input-list-content">
                            <input 
                                className='settings-input' 
                                id={'password'} 
                                value={password}
                                placeholder="Type your password"
                                type={secureInput[k] ? 'text' : 'password'}
                                onChange={(e) => this.handlePasswordChange(e)} 
                            />
                        </div>
                        <div className="remove-btn-content">
                            <button 
                                className="secureToggleButton" 
                                onClick={() => toggleSecureInput(k)}
                                {... (!secureInput[k] ? {'data-secure': true} : {})}
                                > 
                                <span className="material-icons">{!secureInput[k] ? 'visibility' : 'visibility_off'}</span>
                            </button>
                        </div>
                    </div>
                    <br />
                    <button 
                        className="login-button" 
                        type="submit"
                        onClick={(e) => this.handleLoginSubmit(e)}
                    >
                        Login
                    </button>
                </form>
            </div>
        );
    }
};

export default LoginComponent;