var user;

$("#messageToSend").focusin(function() {
    $("#send-box").animate({"border-radius": "1px"});
});

$("#messageToSend").focusout(function() {
    $("#send-box").animate({"border-radius": "20px"});
});

// START WEBSOCKETS
var supportsWebSockets = ('WebSocket' in window || 'MozWebSocket' in window) && WebSocket;
if(!supportsWebSockets){
    $(".very-old-browser-notification").show();
    $(".non-error").hide();
}else{
    $(".very-old-browser-notification").hide();
    $(".non-error").show();
}
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";

// Calls the websocket connect channel
var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat/stream/test-chat");


$("#messageToSend").keypress(function (e) {
    var key = e.which;
    if (key == 13)  // trigger message send when 'enter' key is clicked
    {
        $('#messageSendButton').trigger('click');
        return false;
    }
});

// Code that is called when the socket is succesfully opened
chatsock.onopen = function(message) {
    $('.error-notification').hide();
    $('.non-error').show();
    $('#messages-container').html('<div  class="empty-div"></div>');

    message = {}
    message.command= 'start'
    chatsock.send(JSON.stringify(message)); // START TALKING!
}

chatsock.onmessage = function(message){
    var content_data = JSON.parse(message.data);

    if (content_data['type'] == 'text') {
        processAndDisplayChatMessage(message);
    }
    else if (content_data['type'] == 'complaintSaveStatus') {
        console.log(content_data['text'])
    }
};

chatsock.onclose = function(message){
    message = {}
    message.command= 'leave';
    message.userid = user;

    chatsock.send(JSON.stringify(message));
    console.log("connection lost ... ");
}

chatsock.onerror = function(message){
    console.log("Error reconnecting ... ");
    $('.error-notification').html("Unable to connect to the metsys server. Please try again in a few minutes (by refreshing the page).")
    $('.error-notification').show();
    $('.non-error').hide();
    $("#body-container").scrollTop( $('#body-container')[0].scrollHeight);
    $("#feedbackClose").trigger('click');
}

// Don't show this again functionality for #helpModal
$('#helpModal').on('hidden.bs.modal', function() {
    var status = $("input[name=neverHelp]", this).is(":checked");

    // Omitted domain for local development use
    // If ever used in production, use domain specific cookie
    Cookies.set('help_dismiss', status, {
        expires: 7,
        path: ''
    });
});

$('#helpModal').on('show.bs.modal', function() {
    var status = Cookies.get('help_dismiss');

    // Omitted domain for local development use
    // If ever used in production, use domain specific cookie
    if (status == 'true') {
        $("input[name=neverHelp]", this).attr("checked", "checked");
    }
});


$(document).ready(function() {
    $("#body-container").scrollTop( $('#body-container')[0].scrollHeight);

    if(Cookies.get('help_dismiss') != 'true') {
        $('#helpModal').modal('show');
    }
});
