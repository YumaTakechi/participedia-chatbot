class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.state = false;
        this.messages = [];
        this.isFirstInteraction = true; // Track if it's the first interaction
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        if (!openButton || !chatBox || !sendButton) {
            console.error("❌ ERROR: One or more chatbot elements not found!");
            return;
        }

        // Add click event to the chatbox icon
        openButton.addEventListener('click', () => {
            console.log("Chatbox icon clicked!");
            this.toggleState(chatBox);

            // Show welcome message on first interaction
            if (this.isFirstInteraction) {
                this.showWelcomeMessage(chatBox);
                this.isFirstInteraction = false;
            }
        });

        // Add click event to the send button
        sendButton.addEventListener('click', () => {
            console.log("Send button clicked!");
            this.onSendButton(chatBox);
        });

        // Add Enter key event to the input field
        const node = chatBox.querySelector('input');
        if (node) {
            node.addEventListener("keyup", ({ key }) => {
                if (key === "Enter") {
                    console.log("Enter key pressed!");
                    this.onSendButton(chatBox);
                }
            });
        }
    }

    toggleState(chatBox) {
        this.state = !this.state;
        chatBox.classList.toggle('chatbox--active', this.state);
        console.log("Chatbox state toggled:", this.state);
    }

    showWelcomeMessage(chatBox) {
        const welcomeMessage = {
            name: "Participedia",
            message: `
                <strong>Chatbot:</strong> Hey there! 🌟<br>
                Welcome to Participedia—your go-to guide for all things participatory democracy and citizen engagement. How can I assist you today? Are you looking for a specific case, method, or just curious to explore? Let’s dive in! 🌟<br><br>
                <strong>Quick Options:</strong><br>
                <button class="quick-option" data-prompt="Tell me about election cases in Canada">Election Cases</button>
                <button class="quick-option" data-prompt="What are some participatory budgeting examples?">Participatory Budgeting</button>
                <button class="quick-option" data-prompt="Show me citizen assemblies">Citizen Assemblies</button>
            `
        };

        this.messages.push(welcomeMessage);
        this.updateChatText(chatBox);

        // Add click event to quick option buttons
        const quickOptions = chatBox.querySelectorAll('.quick-option');
        quickOptions.forEach(button => {
            button.addEventListener('click', () => {
                const prompt = button.getAttribute('data-prompt');
                this.onQuickOptionSelected(chatBox, prompt);
            });
        });
    }

    onQuickOptionSelected(chatBox, prompt) {
        const inputField = chatBox.querySelector('input');
        inputField.value = prompt; // Set the prompt in the input field
        this.onSendButton(chatBox); // Simulate sending the prompt
    }

    onSendButton(chatBox) {
        const textField = chatBox.querySelector('input');
        const userInput = textField.value.trim();

        if (userInput === "") {
            console.warn("⚠️ WARNING: Empty message, not sending.");
            return;
        }

        console.log("Sending message:", userInput);

        // Add user message to chat history
        const userMessage = { name: "User", message: userInput };
        this.messages.push(userMessage);
        this.updateChatText(chatBox);

        // Fetch case search results
        const caseSearchPromise = fetch('http://127.0.0.1:8000/search_cases', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_query: userInput,
                conversation_history: this.messages.filter(msg => msg.name === "User").map(msg => ({ role: "user", message: msg.message }))
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log("API Response:", data); // Log the API response
                if (data.error) {
                    throw new Error(data.error);
                }
                return data.results; // Return the pre-formatted HTML string
            })
            .catch(error => {
                console.error("❌ ERROR:", error);
                return ""; // Return an empty string in case of error
            });

        // Fetch DeepSeek response via OpenRouter
        const deepseekPromise = fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer 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', // Replace with your OpenRouter API key
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: "deepseek/deepseek-chat:free",
                messages: [
                    { role: "system", content: "You are a friendly chatbot." },
                    ...this.messages.map(msg => ({
                        role: msg.name === "User" ? "user" : "assistant",
                        content: msg.message
                    })),
                    { role: "user", content: userInput }
                ]
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("DeepSeek API Response:", data);
                if (!data.choices || data.choices.length === 0) {
                    throw new Error("No response from DeepSeek.");
                }
                return data.choices[0].message.content;
            })
            .catch(error => {
                console.error("❌ ERROR:", error);
                return "I'm having trouble generating a response.";
            });

        // Wait for both responses and combine them
        Promise.all([caseSearchPromise, deepseekPromise])
            .then(([caseResults, deepseekResponse]) => {
                console.log("Resolved Case Results:", caseResults); // Log the resolved caseResults
                let combinedMessage = `<strong>Chatbot:</strong> ${deepseekResponse}`;
                if (caseResults) {
                    combinedMessage += `<br><br><strong>Case Search Results:</strong><br>${caseResults}`;
                } else {
                    console.warn("⚠️ WARNING: No valid case search results found.");
                }

                // Add bot response to chat history
                const botMessage = { name: "Participedia", message: combinedMessage };
                this.messages.push(botMessage);
                this.updateChatText(chatBox);

                textField.value = ''; // Clear input
            })
            .catch(error => {
                console.error("❌ ERROR in Promise.all:", error);
            });
    }

    updateChatText(chatBox) {
        const chatMessage = chatBox.querySelector('.chatbox__messages');
        if (!chatMessage) return;

        // Clear the messages container
        chatMessage.innerHTML = '';

        // Add each message as a separate div
        this.messages.forEach(item => {
            const isBot = item.name === "Participedia";
            const messageDiv = document.createElement('div');
            messageDiv.className = `messages__item messages__item--${isBot ? "visitor" : "operator"}`;
            messageDiv.innerHTML = item.message;
            chatMessage.appendChild(messageDiv);
        });

        // Scroll to the bottom
        chatMessage.scrollTop = chatMessage.scrollHeight;
    }
}

// Initialize the chatbox after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const chatbox = new Chatbox();
    chatbox.display();
});