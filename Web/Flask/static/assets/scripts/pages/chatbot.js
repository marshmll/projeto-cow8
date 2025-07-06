// Default white font color for chart.
Chart.defaults.color = "#ffffff";

document.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");

  // Auto-resize textarea
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = `${Math.min(userInput.scrollHeight, 128)}px`;
  });

  // Format message content
  const formatContent = (content) => {
    const replacements = [
      // Headers
      [/^###\s+(.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>'],
      [/^##\s+(.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>'],
      [/^#\s+(.*$)/gm, '<h1 class="text-2xl font-semibold mt-4 mb-2">$1</h1>'],

      // Code blocks
      [
        /```([\s\S]*?)```/g,
        (_, code) =>
          `<pre class="bg-gray-700 rounded-md p-3 overflow-x-auto my-2"><code>${code.trim()}</code></pre>`,
      ],

      // Inline elements
      [
        /`([^`]+)`/g,
        '<code class="bg-gray-700 rounded px-1 py-0.5 text-sm">$1</code>',
      ],
      [/\*\*(.*?)\*\*/g, "<strong>$1</strong>"],
      [/\*(.*?)\*/g, "<em>$1</em>"],
      [
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank" class="text-blue-400 hover:underline">$1</a>',
      ],

      // Lists
      [/^(\d+)\.\s+(.*$)/gm, "<li>$2</li>"],
      [/\n/g, "<br>"],
    ];

    let formatted = content;
    replacements.forEach(([regex, replacement]) => {
      formatted = formatted.replace(regex, replacement);
    });

    if (formatted.includes("<li>")) {
      formatted = formatted.replace(/<br><li>/g, "<li>");
      formatted = `<ol class="list-decimal pl-5 space-y-1 my-2">${formatted}</ol>`;
    }

    return formatted;
  };

  // Add message to chat
  const addMessage = (role, content) => {
    const messageDiv = document.createElement("div");
    messageDiv.className = `flex ${
      role === "user" ? "justify-end" : "justify-start"
    }`;

    const messageContent = document.createElement("div");
    messageContent.className = `text-white p-4 max-w-[85%] sm:max-w-[75%] shadow-md ${
      role === "user" ? "message-user" : "message-ai"
    }`;

    messageContent.innerHTML =
      role === "user"
        ? formatContent(content)
        : `
        <div class="flex items-start">
          <div class="flex-shrink-0 mr-3 text-gray-400">
            <i class="fas fa-robot"></i>
          </div>
          <div class="text-sm sm:text-base">${formatContent(content)}</div>
        </div>
      `;

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  // Add chart
  const addChart = (role, content) => {
    if (!content) return;

    const messageDiv = document.createElement("div");
    messageDiv.className = `flex ${
      role === "user" ? "justify-end" : "justify-start"
    }`;

    const messageContent = document.createElement("div");
    messageContent.className = `text-white p-4 min-w-[85%] min-h-[25rem] sm:min-w-[75%] shadow-md ${
      role === "user" ? "message-user" : "message-ai"
    }`;

    if (content.includes("canvas")) {
      messageContent.innerHTML = `
      <div class="message-ai text-white p-4 w-[100%] h-[100%] min-w-[35rem] min-h-[20rem] shadow-md relative">
        <div class="flex items-start">
          <div class="flex-shrink-0 mr-3 text-gray-400">
            <i class="fas fa-robot"></i>
          </div>
          <div class="w-full overflow-auto max-h-[70vh] relative">
            ${content}
            <button title="Baixar gráfico como imagem" class="downloadChartBtn absolute top-2 right-2 bg-blue-600 opacity-25 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded-full shadow-lg transition-all duration-200 ease-in-out transform hover:scale-105 flex items-center gap-1 text-sm">
              <i class="fas fa-download text-xs"></i>
            </button>
          </div>
        </div>
      </div>
      `;

      // Add download chart functionality to the button
      const canvas = messageContent.querySelector("canvas");
      const downloadChartBtn =
        messageContent.querySelector(".downloadChartBtn");
      downloadChartBtn.id = `download_${canvas.id}`;

      downloadChartBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const canvasId = e.currentTarget.id.substring(9);
        const canvas = document.getElementById(canvasId);
        const link = document.createElement("a");
        link.download = `${canvas.id}.png`;
        link.href = canvas.toDataURL("image/png");
        link.click();
      });

      // Extract and execute the script with our styling
      const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
      if (scriptMatch && scriptMatch[1]) {
        setTimeout(() => {
          try {
            // Store the original Chart object
            const originalChart = window.Chart;

            // // Create our own Chart wrapper
            window.Chart = function (ctx, config) {
              return new originalChart(ctx, {
                ...config,
                options: {
                  ...getChartOptions(),
                },
              });
            };
            window.Chart.prototype = originalChart.prototype;

            // Now execute the script
            new Function(scriptMatch[1])();

            // Restore original Chart
            window.Chart = originalChart;
          } catch (e) {
            console.error("Error executing chart script:", e);
          }
        }, 0);
      }
    } else {
      addMessage(role, content);
      return;
    }

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  // Define chart options locally
  const getChartOptions = () => ({
    responsive: true,
    scales: {
      x: {
        grid: {
          color: "#909090",
          borderColor: "rgba(200, 200, 200, 0.8)",
        },
        ticks: { color: "#ffffff" },
        title: { color: "#ffffff" },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: "#909090",
          borderColor: "rgba(200, 200, 200, 0.8)",
        },
        ticks: { color: "#ffffff" },
        title: { color: "#ffffff" },
      },
    },
    plugins: {
      legend: {
        labels: { color: "#ffffff" },
      },
    },
  });

  // Typing indicator
  const showTyping = () => {
    const typingDiv = document.createElement("div");
    typingDiv.className = "flex justify-start";
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = `
      <div class="message-ai text-white p-4 max-w-[85%] sm:max-w-[75%] shadow-md">
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
      </div>
    `;
    chatMessages.appendChild(typingDiv);
  };

  const hideTyping = () => {
    document.getElementById("typing-indicator")?.remove();
  };

  // Form submission
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Clear input and show user message
    addMessage("user", message);
    userInput.value = "";
    userInput.style.height = "auto";
    showTyping();

    try {
      const response = await fetch("/api/chatbot/prompt/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: message }),
      });

      if (!response.ok) {
        // Handle HTTP errors
        const errorText = await response.text();
        let errorMessage = "Desculpe, ocorreu um erro no servidor.";

        try {
          // Try to parse error response if it's JSON
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.response || errorJson.error || errorMessage;
        } catch {
          // If not JSON, use raw text
          errorMessage = errorText || errorMessage;
        }

        throw new Error(errorMessage);
      }

      const json = await response.json();
      hideTyping();

      // Handle API response errors
      if (!json?.success) {
        const errorMessage =
          json?.response || json?.error || "Resposta inválida do servidor";
        addMessage("assistant", `${errorMessage}`);

        // Optionally show the failed query if available
        if (json?.query) {
          const errorDetails = document.createElement("div");
          errorDetails.className = "text-xs text-gray-400 mt-2";
          errorDetails.textContent = `Consulta: ${json.query}`;
          document
            .querySelector(".message-ai:last-child")
            .appendChild(errorDetails);
        }

        console.log(json);

        return;
      }

      // Successful response handling
      if (json?.response?.length > 0) {
        addMessage("assistant", json.response);
      }

      if (json?.graphic?.length > 0) {
        try {
          addChart("assistant", json.graphic);
        } catch (chartError) {
          console.error("Chart rendering failed:", chartError);
          addMessage(
            "assistant",
            "O gráfico não pôde ser exibido, mas aqui estão os dados:"
          );
          if (json?.response?.length > 0) {
            // Re-show the response if chart failed
            addMessage("assistant", json.response);
          }
        }
      }
    } catch (error) {
      hideTyping();

      // Classify different error types
      let userMessage =
        "Desculpe, ocorreu um erro. Por favor, tente novamente.";

      if (
        error instanceof TypeError &&
        error.message.includes("Failed to fetch")
      ) {
        userMessage =
          "Erro de conexão. Verifique sua internet e tente novamente.";
      } else if (
        error.message.includes("timeout") ||
        error.message.includes("Timeout")
      ) {
        userMessage = "A requisição demorou muito. Tente novamente mais tarde.";
      }

      addMessage("assistant", userMessage);

      // Log full error for debugging
      console.error("Error details:", {
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        userInput: message,
      });
    }
  });

  // Shortcuts
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  userInput.focus();
});
