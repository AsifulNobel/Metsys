var user;
var accessTopicsEn = 0;
var totalTopicsEn = 0;
var accessTopicsBn = 0;
var totalTopicsBn = 0;

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
        checkTag(content_data['tag']);
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

function updateTopicNumbers() {
    banglaElems = $('.bangla-topics');
    englishElems = $('.english-topics');
    totalTopicsBn = banglaElems.length;
    totalTopicsEn = englishElems.length;
    accessTopicsBn = 0;
    accessTopicsEn = 0;

    for(var i=0; i < totalTopicsEn; i++) {
        if (englishElems[i].className.indexOf('fa-check-circle-o') != -1) {
            accessTopicsEn++;
        }
    }

    for(var i=0; i < totalTopicsBn; i++) {
        if (banglaElems[i].className.indexOf('fa-check-circle-o') != -1) {
            accessTopicsBn++;
        }
    }

    $('#bangla-stat').html('Accessed Topics:  '.concat(accessTopicsBn.toString()).concat(' Total Topics: ').concat(totalTopicsBn.toString()));
    $('#english-stat').html('Accessed Topics:  '.concat(accessTopicsEn.toString()).concat(' Total Topics: ').concat(totalTopicsEn.toString()));
}

$('#banglaTopic').on('show.bs.modal', updateTopicNumbers);
$('#englishTopic').on('show.bs.modal', updateTopicNumbers);

function checkTag(tag) {
    var en = 'english';
    var bn = 'bangla';
    var language;
    var actualTag;
    var message;
    var funnyMessage = [
        '10 Points to Gryffindor',
        'Keep going, bruh. You are killing it!',
        'What are you on tonight? Whatever it is, please send a kilo of it to my address',
        'First Rule of Alpha Testing, don\'t talk about Alpha Testing',
        'Work it like you mean it',
        'They said it was a team project. It is a team of one, they never said',
        'Friends?',
        'Thousand Points to Gryffindor',
    ];
    var randomNumber = Math.floor(Math.random()*funnyMessage.length);

    if (tag.length) {
        if (tag.indexOf(en) != -1) {
            language = en.toUpperCase();
        }
        else {
            language = bn.toUpperCase();
        }
        actualTag = tag.slice((tag.indexOf('_')+1), );

        message = language.concat(' Agent\'s "'.concat(actualTag)).concat('" topic');
    }

    if (tag != "") {
        if (!$('#'.concat(tag)).hasClass('fa-check-circle-o')) {
            $('#'.concat(tag)).addClass('fa-check-circle-o').removeClass('fa-circle-o');
            toastr.info(funnyMessage[randomNumber]);
            toastr.success('You have accessed '.concat(message));
        }
    }
}

$(document).ready(function() {
    $("#body-container").scrollTop( $('#body-container')[0].scrollHeight);

    if(Cookies.get('help_dismiss') != 'true') {
        $('#helpModal').modal('show');
    }

    toastr.options.closeButton = true;

    updateTopicNumbers();
});
