document.addEventListener("DOMContentLoaded", function() {
    let dropArea = document.querySelector(".drop-area");
    let userInput = document.getElementById("user-input");
    let sendBtn = document.getElementById("send-btn");
    let messageContainer = document.getElementById("messages");
    let fileElem = document.getElementById("fileElem");

    // Herhangi bir yere bırakıldığında dosya eklenmesini sağlamak
    document.addEventListener("dragover", function(e) {
        e.preventDefault();
        dropArea.classList.add("highlight");
    });

    document.addEventListener("dragleave", function(e) {
        dropArea.classList.remove("highlight");
    });

    document.addEventListener("drop", function(e) {
        e.preventDefault();
        dropArea.classList.remove("highlight");
        let files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });

    dropArea.addEventListener("dragover", function(e) {
        e.preventDefault();
        dropArea.classList.add("highlight");
    });

    dropArea.addEventListener("dragleave", function() {
        dropArea.classList.remove("highlight");
    });

    dropArea.addEventListener("drop", function(e) {
        e.preventDefault();
        dropArea.classList.remove("highlight");
        let files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });

    fileElem.addEventListener("change", function() {
        if (fileElem.files.length > 0) {
            handleFiles(fileElem.files);
        }
    });

    function handleFiles(files) {
        let formData = new FormData();
        formData.append("file", files[0]);
        uploadFile(formData, files[0]);
    }

    function uploadFile(formData, file) {
        if (!formData) {
            formData = new FormData();
            formData.append("file", file);
        }

        let reader = new FileReader();
        reader.onload = function(e) {
            let img = document.createElement("img");
            img.src = e.target.result;
            img.classList.add("image-preview");

            let userMessage = document.createElement("div");
            userMessage.classList.add("message", "user");
            userMessage.innerHTML = `<div class="icon"><img src="/static/user.png" alt="User" width="30" height="30"></div>`;
            userMessage.appendChild(img);
            messageContainer.appendChild(userMessage);
            messageContainer.scrollTop = messageContainer.scrollHeight;
        };
        reader.readAsDataURL(file);

        fetch("/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error:", data.error);
                return;
            }
            let botMessage = document.createElement("div");
            botMessage.classList.add("message", "bot");
            botMessage.innerHTML = `<div class="icon"><img src="/static/bot.png" alt="Bot" width="30" height="30"></div><div class="message-content"></div>`;
            messageContainer.appendChild(botMessage);

            let result = `<h2>Image Analysis Result</h2>
                          <p><strong>Description:</strong> ${data.description}</p>
                          <p><strong>GTIP Code:</strong> ${data.gtip_code}</p>`;
            let container = document.createElement("div");
            container.innerHTML = result;
            let text = container.innerText;
            let index = 0;
            function typeWriter() {
                if (index < text.length) {
                    botMessage.children[1].textContent += text.charAt(index);
                    index++;
                    setTimeout(typeWriter, 20); // Yazma hızını artırmak için süreyi azaltıyoruz
                } else {
                    // HTML içeriği doğru bir şekilde ekleyelim
                    botMessage.children[1].innerHTML = result;
                }
            }
            typeWriter();
            messageContainer.scrollTop = messageContainer.scrollHeight;
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    sendBtn.addEventListener("click", function() {
        sendMessage();
    });

    userInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        let userInputValue = userInput.value;
        if (!userInputValue.trim()) return;
        userInput.value = '';

        let userMessage = document.createElement("div");
        userMessage.classList.add("message", "user");
        userMessage.innerHTML = `<div class="icon"><img src="/static/user.png" alt="User" width="30" height="30"></div><div class="message-content">${userInputValue}</div>`;
        messageContainer.appendChild(userMessage);
        messageContainer.scrollTop = messageContainer.scrollHeight;

        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "message": userInputValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error:", data.error);
                return;
            }
            let botMessage = document.createElement("div");
            botMessage.classList.add("message", "bot");
            botMessage.innerHTML = `<div class="icon"><img src="/static/bot.png" alt="Bot" width="30" height="30"></div><div class="message-content"></div>`;
            messageContainer.appendChild(botMessage);

            let container = document.createElement("div");
            container.innerHTML = data.message;
            let text = container.innerText;
            let index = 0;
            function typeWriter() {
                if (index < text.length) {
                    botMessage.children[1].textContent += text.charAt(index);
                    index++;
                    setTimeout(typeWriter, 20); // Yazma hızını artırmak için süreyi azaltıyoruz
                } else {
                    // HTML içeriği doğru bir şekilde ekleyelim
                    botMessage.children[1].innerHTML = data.message;
                }
            }
            typeWriter();
            messageContainer.scrollTop = messageContainer.scrollHeight;
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }
});
