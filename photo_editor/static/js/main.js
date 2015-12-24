$(document).ready(function () {
    /*
    |-------------------------------------------------
    | Facebook Authentication
    |-------------------------------------------------
    */
	$('.login-wrapper').on('click', fbLogin);
});

var fbLogin = function () {
    FB.getLoginStatus(function (response) {
        if (response.status === 'connected') {
            window.location = '/';
        } else {
            FB.login(function (response) {
                if (response.authResponse) {
                    console.log('Welcome!  Fetching your information.... ');
                    //get access token
                    access_token = response.authResponse.accessToken;
                    //get FB UID
                    user_id = response.authResponse.userID;
                    FB.api('/me', function (response) {
                        //get user email
                        user_email = response.email;
	                   // you can store this data into your database
                        window.location = '/';
                    });
                } else {
                    //user hit cancel button
                    console.log('User cancelled login or did not fully authorize.');
                }
            }, 
            {scope:$('.facebook').attr('data-scope')});
        }
    });
};
