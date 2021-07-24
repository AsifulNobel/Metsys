function generate_formatted_chat_message(data){
	// Function to simply format the message text
	if(data.type == 'text'){
		message_text = '<span>' + data.text + '</span>'
		return message_text;
	}
	console.log("invalid data format");
	return "";
}

// Function that adds a message to the chat window
function add_message_to_chat(data, formatted_div){
	var chat = $('#messages-container');
	var new_source = data["source"];

	if (new_source == "BOT"){
		chat.append('<div class="msg-row"><div class="col-xs-11 col-sm-11 col-md-11 col-lg-11 no-sides-padding msg-animate"><div class="panel message-panel bot-msg "><div class="panel-body bot-msg-body"><div><div class="message-text">'+formatted_div+'</div></div></div></div><div class="bot-msg-bubble">Bot</div></div><div class="col-xs-1 col-sm-1 col-md-1 col-lg-1 no-sides-padding msg-animate complaint-mark" onclick="complaint(this)"><i class="fa fa-times-circle-o" aria-hidden="true"></i></div></div>');
	}else if(new_source == "CANDIDATE"){

		var child = $('<div class="msg-row">');
		$(child).append('<div class="row"><div class="col-xs-10 col-sm-10 col-md-10 col-lg-10  pull-right no-sides-padding msg-animate user-msg"><div class="panel message-panel"><div class="panel-body user-msg-body"><div class="message-text">'+formatted_div+'</div></div></div><div class="user-msg-bubble">you</div></div>');
		chat.append(child);
	}
	$("#body-container").scrollTop( $('#body-container')[0].scrollHeight);
}


function processAndDisplayChatMessage(message){
	// Function that is called when the server sends a message via websockets to front end.

	if (message.data) {
		// Bot Message
		var content_data = JSON.parse(message.data);
	}
	else {
		// User message
		var content_data = message
	}
	var formatted_div = generate_formatted_chat_message(
		content_data);

	if(formatted_div.length > 0){
		add_message_to_chat(content_data, formatted_div);
	}
}


function sendTextMessage() {
	// Gets called when user tries to send a message to bot
	// The message is formatted in a object with appropriate command &
	// sent to bot
    if ($('#messageToSend').text() == "") {
        return
    }

    message = {}
    message.text = $('#messageToSend').html().replace("</div>", "").replace("<div>", "\n").replace("<br>", "\n");

	if (message.text.indexOf('span') > -1) {
		tempText = message.text.slice(message.text.indexOf('>')+1, message.text.indexOf('</'));

		message.text = tempText;
	}

	while(message.text.indexOf('&nbsp;') != -1) {
		message.text = message.text.replace('&nbsp;', '');
	}

	while(message.text.indexOf('\n') != -1) {
		message.text = message.text.replace('\n', '');
	}

    message.command= 'send'
    message.timestamp = new Date();

	message_to_send_content = {
        'text': message['text'],
        'type': 'text',
        'source': 'CANDIDATE'
    }

    $('#messageToSend').text('');
	chatsock.send(JSON.stringify(message));
	// Displays user message
	processAndDisplayChatMessage(message_to_send_content);
	$("#message").val('').focus();
    return false;
}

function feedbackErrorMessage(message) {
	// adds error message to feedback modal
	var feedbackElement = $('#feedbackModalForm')
	var feedbackForm = feedbackElement.html()

	if ($("#comment-error").length == 0)
		feedbackElement.html(feedbackForm+message)
}

// Function that is called when a feedback is submitted
function sendFeedback() {
	if ($('#comments').val() == "") {
		feedbackErrorMessage('<div class="form-group"><p class="text-danger" id="comment-error">Comments, there must be</p></div>')
        return
    }

	var feedback = {}

	if ($("#userName").val() !== "")
		feedback.name = $("#userName").val()
	else
		feedback.name = "anonymous"
	feedback.comment = $("#comments").val()
	feedback.command = "feedback"

	// TODO: Fix security vulnerability for input
	$("#userName").val("")
	$("#comments").val("")

	chatsock.send(JSON.stringify(feedback))

	if ($("#comment-error").length > 0) {
		$("#comment-error").remove()
	}

	$("#feedbackClose").trigger('click')

	return
}

function getMessagePair(element) {
	// Gets bot message from element and user message from previous msg-row div,
	// then bundles it in a JS object
	botMessageDiv = $(element).parent()
	userMessageDiv = $(botMessageDiv).prev()
	botMessageText = $(botMessageDiv).find('.message-text span').html()
	userMessageText = $(userMessageDiv).find('.message-text span').html()

	messagePair = {}
	messagePair.userMessageText = userMessageText
	messagePair.botMessageText = botMessageText

	console.log(messagePair)
	return messagePair
}

function complaint(element) {
	// Creates complaint or deletes complaint based on state
	if ($(element).children().first().hasClass("fa-times-circle-o")) {
		$('#confirm').modal({
      		backdrop: 'static',
      		keyboard: false
    	})
    	.on('click', '#yes', function(e) {
      		makeComplaint(element)
    	});
	}
}


function makeComplaint(element) {
	$(element).children().removeClass('fa-times-circle-o')
	$(element).children().addClass('fa-times-circle')

	messagePair = getMessagePair(element)
	complaint_message = {}
	complaint_message.messagePair = messagePair
	complaint_message.command = "complain"

	chatsock.send(JSON.stringify(complaint_message))
}
