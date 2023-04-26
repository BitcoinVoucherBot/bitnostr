import { Component } from "react"

class StatusComponent extends Component {

    render() {
        const { status, settings, checkIfRelayIsConnected, stopBot, startBot } = this.props
        return (
            <div className='status-container'>
                <div>
                    <div className='status-item'>
                        <span className='status' id='status' status={status}>{status}</span>
                    </div>
                    <div className='relays-list'>
                    {Object.entries(settings.relays).map(([key, value]) => (
                        <div key={key} className="relay-item frosty">
                            <span className='connected-relay' id={key} {... (checkIfRelayIsConnected(value) ? {'data-connected': true} : {})}>{value}</span>
                        </div>
                    ))}
                    </div>
                    {status === 'RUNNING' ? (
                    <div>
                        <button className="button to_stop" onClick={() => stopBot(false)}>Stop bot</button>
                    </div>
                    ) : (
                    <div>
                        <button className="button to_start" onClick={() => startBot(false)}>Start bot</button>
                    </div>
                    )}
                </div>
            </div>
        )
    }
}

export default StatusComponent