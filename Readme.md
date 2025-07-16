Simple Real-time Chat Application (WhatsApp Clone) 💬
This is a basic real-time chat application designed to mimic some core functionalities of WhatsApp, including public and private messaging, an active user list, and typing indicators. It consists of a Python WebSocket server and an HTML/JavaScript client.

Features ✨
Real-time Public Chat: Send and receive messages instantly in a public channel. Senders now see their own messages immediately. 🚀

Private Messaging: Send direct messages to specific online users. 🔒

Active Users List: See who is currently online in a dedicated sidebar. 👀

User Join/Leave Notifications: System messages announce when users connect or disconnect. 👋🚪

Typing Indicator: See when other users are actively typing a message. ✍️

Message Timestamps: Each message is displayed with the time it was sent. ⏰

Enhanced UI: A cleaner, more modern, and visually appealing user interface inspired by chat applications. 🎨✨

Separate Username Input: A dedicated screen for entering your username before joining the chat. 👤

Emoji Support: Send and receive emojis seamlessly as part of your messages. 😄👍🎉

Technologies Used 💻
Backend: Python 3 (with websockets library)

Frontend: HTML5, CSS3 (Tailwind CSS for utility classes), JavaScript

Icons: Font Awesome

Setup and Installation 🛠️
To run this application, you need Python 3 installed on your system.

1. Clone or Download the Project 📂
Ensure you have both server.py and chat_client.html files in the same directory.

2. Install Python Dependencies ⬇️
Open your terminal or command prompt and navigate to the project directory. Install the websockets library:

pip install websockets

3. Run the Python Server ▶️
In your terminal, from the project directory, execute the server script:

python server.py

You should see a message indicating that the server has started, for example:
INFO:root:WebSocket server started on ws://localhost:8765

Keep this terminal window open and the server running throughout your chat session.

4. Open the HTML Client 🌐
Important: The chat_client.html file must be opened as a local file in your web browser. Do NOT try to navigate to http://localhost:8765 directly in your browser's address bar for the client.

To open the client:

Method 1 (Recommended): Go to the directory where you saved chat_client.html using your file explorer (e.g., Windows Explorer, macOS Finder). Double-click on chat_client.html. It will open in your default web browser.

Method 2 (From Browser): Open your web browser (Chrome, Firefox, Edge, etc.). Go to File > Open File... (or similar, depending on your browser). Navigate to your project directory and select chat_client.html.

The address bar in your browser should show a file:/// path (e.g., file:///C:/Users/YourUser/Documents/chat_app/chat_client.html).

How to Use 🧑‍💻
Enter Username: Upon opening chat_client.html, you will be greeted by a welcome screen. Enter your desired username and click "Start Chat". 👋

Join Chat: The welcome screen will disappear, and the main chat interface will load. 💬

Public Messaging: Type your message in the input field at the bottom and press Enter or click the send button. Your message will appear immediately in your chat, and all other connected users will also see it. 🗣️

Private Messaging:

To send a private message, click on a username in the "Active Users" list on the left sidebar. 🤫

A "Private message to: [username]" indicator will appear above your message input field.

Type your message and send it. Only the selected recipient will receive it, and you will see it in your chat marked as private. ✉️

To switch back to public chat, click the "x" button next to the private message indicator. 🔄

Typing Indicator: When another user is typing, you will see a "[Username] is typing..." message above your message input field. ✏️

Emoji Input: Use your operating system's built-in emoji picker (e.g., Win + . or Win + ; on Windows, Ctrl + Cmd + Space on macOS) to insert emojis directly into the message input field. 😊

Multiple Clients: To test the real-time functionality, open chat_client.html in multiple browser tabs or windows on the same system, using a different username for each. You will see all messages, join/leave notifications, and typing statuses reflected across all open clients. 👯

Troubleshooting 🐛
"Enter Your Username" screen not closing / Connection Errors:

Ensure your server.py is running in a terminal and shows "WebSocket server started on ws://localhost:8765". ✅

Crucially, ensure you are opening chat_client.html as a file:/// URL (local file) and not attempting to access it via an http:// or ws:// address. ⚠️

Check your browser's Developer Tools (F12, then Console tab) for any red error messages. These messages are critical for diagnosing the problem. 🐞

If you encounter persistent issues, please provide the exact error messages from your browser's developer console and your Python server's terminal. 🙏