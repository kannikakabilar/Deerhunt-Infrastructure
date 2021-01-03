class ScrimmageButton extends React.Component {
    constructor() {
        super();
    }

    scrimmage() {
        const requestData = JSON.stringify({
            "target_team": this.props.team,
        });

        $.ajax({
            url: '/api/scrimmage',
            type: 'POST',
            data: requestData,
            contentType: 'application/json',
            success: (responseData) => {
                this.props.reloadCallback();

            },
            error: (err) => {
                console.log(err);
                this.props.errorCallback("fail_accept");
            }
        });
    }
    render() {
        return (
            <div className="leaderboard-button" onClick={this.scrimmage.bind(this)}>Scrimmage</div>
        );
    }
}

export default ScrimmageButton;