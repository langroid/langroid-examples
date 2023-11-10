document.addEventListener("DOMContentLoaded", function () {
    const chatArea = document.getElementById("chat-area");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");

    // Function to add a message to the chat area
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", isUser ? "user-message" : "bot-message");
        messageDiv.textContent = message;
        chatArea.appendChild(messageDiv);
    }

    // Function to send a message to the server and receive a response
    function sendMessageToServer() {
        const message = userInput.value;

        // Add the user message to the chat area
        addMessage(message, true);

        // Create a JSON object with the user input
        const requestData = { "prompt": message };

        // Make an AJAX request to the server with JSON data
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/langroid/agent/completions", true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);

                // Display the response from the server
                const botMessage = response.message;
                addMessage(botMessage);

                // Clear the user input field
                userInput.value = "";
            }
        };

        const data = JSON.stringify(requestData);
        xhr.send(data);
    }

    // Event listener for the "Send" button
    sendButton.addEventListener("click", function () {
        sendMessageToServer();
    });

    // Event listener for pressing the Enter key in the input field
    userInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent the default form submission
            sendMessageToServer();
        }
    });
});
