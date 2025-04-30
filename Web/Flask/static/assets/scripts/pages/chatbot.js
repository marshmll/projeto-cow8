document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");

    // Auto-resize textarea as user types
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = `${Math.min(userInput.scrollHeight, 128)}px`;
    });

    function formatContent(content) {
        // Convert headers (###) to <h3>
        content = content.replace(
            /^###\s+(.*$)/gm,
            '<h3 class="text-lg font-semibold mt-4 mb-2 text-wrap">$1</h3>'
        );

        // Convert code blocks (```) to <pre><code>
        content = content.replace(/```([\s\S]*?)```/g, function (match, code) {
            return `<pre class="bg-gray-700 rounded-md p-3 overflow-x-auto my-2 max-w-full"><code class="text-sm whitespace-pre-wrap break-words">${code.trim()}</code></pre>`;
        });

        // Convert inline code (`) to <code>
        content = content.replace(
            /`([^`]+)`/g,
            '<code class="bg-gray-700 rounded px-1 py-0.5 text-sm whitespace-normal break-words">$1</code>'
        );

        // Convert numbered lists (1. 2. 3.)
        content = content.replace(
            /^(\d+)\.\s+(.*$)/gm,
            '<li class="break-words">$2</li>'
        );

        // Convert **bold** to <strong>
        content = content.replace(
            /\*\*(.*?)\*\*/g,
            '<strong class="break-words">$1</strong>'
        );

        // Convert *italic* to <em>
        content = content.replace(
            /\*(.*?)\*/g,
            '<em class="break-words">$1</em>'
        );

        // Convert line breaks to <br>
        content = content.replace(/\n/g, "<br>");

        // Convert URLs to links
        content = content.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" class="text-blue-400 hover:underline break-all">$1</a>'
        );

        // If content has <li> tags, wrap in <ol>
        if (content.includes("<li>")) {
            content = content.replace(/<br><li>/g, "<li>"); // Clean up
            content = `<ol class="list-decimal pl-5 space-y-1 my-2 break-words">${content}</ol>`;
        }

        return content;
    }

    // Function to add a message to the chat
    function addMessage(role, content) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `flex ${
            role === "user" ? "justify-end" : "justify-start"
        }`;

        const messageContent = document.createElement("div");
        messageContent.className = `text-white p-4 max-w-[85%] sm:max-w-[75%] shadow-md ${
            role === "user" ? "message-user" : "message-ai"
        }`;

        const formattedContent = formatContent(content);

        if (role === "user") {
            messageContent.innerHTML = formattedContent;
        } else {
            messageContent.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0 mr-3 text-gray-400">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="text-sm sm:text-base">${formattedContent}</div>
                </div>
            `;
        }

        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to show typing indicator
    function showTyping() {
        const typingDiv = document.createElement("div");
        typingDiv.className = "flex justify-start";
        typingDiv.id = "typing-indicator";

        const typingContent = document.createElement("div");
        typingContent.className =
            "message-ai text-white p-4 max-w-[85%] sm:max-w-[75%] shadow-md";
        typingContent.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0 mr-3 text-gray-400">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to hide typing indicator
    function hideTyping() {
        const typingIndicator = document.getElementById("typing-indicator");
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Handle form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage("user", message);
        userInput.value = "";
        userInput.style.height = "auto";

        // Show typing indicator
        showTyping();

        try {
            const response = await fetch("/api/chatbot/prompt/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ content: message }),
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const json = await response.json();

            hideTyping();
            addMessage("assistant", json.response);
        } catch (error) {
            hideTyping();
            addMessage(
                "assistant",
                "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
            );
            console.error("Error:", error);
        }
    });

    // Allow sending message with Shift+Enter
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // Focus input on load
    userInput.focus();
});
