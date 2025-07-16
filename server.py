import asyncio
import websockets
import json
import logging
import time # For timestamps

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary to store connected WebSocket clients with their associated usernames
# Key: websocket object, Value: username string
connected_clients = {}

async def send_active_users_list():
    """Sends the current list of active users to all connected clients."""
    active_users = list(connected_clients.values())
    message = {
        "type": "update_users",
        "users": active_users
    }
    await broadcast_message(json.dumps(message))

async def broadcast_message(message_json, exclude_websocket=None):
    """
    Broadcasts a JSON message to all connected clients, optionally excluding one.
    Handles disconnections during broadcast.
    """
    disconnected_clients = []
    for client_ws in connected_clients.keys():
        if client_ws != exclude_websocket:
            try:
                await client_ws.send(message_json)
            except websockets.exceptions.ConnectionClosedOK:
                logging.warning(f"Failed to send to disconnected client during broadcast: {client_ws.remote_address}")
                disconnected_clients.append(client_ws)
            except Exception as e:
                logging.error(f"Error sending broadcast message to {client_ws.remote_address}: {e}")
                disconnected_clients.append(client_ws)
    
    # Clean up disconnected clients after iterating
    for client_ws in disconnected_clients:
        await unregister(client_ws)

async def register(websocket, username):
    """Registers a new client connection with a username."""
    connected_clients[websocket] = username
    logging.info(f"Client connected: {websocket.remote_address} as {username}. Total clients: {len(connected_clients)}")
    
    # Notify all clients that a new user has joined
    join_message = {
        "type": "user_joined",
        "username": username,
        "timestamp": int(time.time() * 1000) # Milliseconds timestamp
    }
    await broadcast_message(json.dumps(join_message))
    
    # Send updated user list to all clients
    await send_active_users_list()

async def unregister(websocket):
    """Unregisters a client connection and notifies others."""
    username = connected_clients.pop(websocket, "Unknown User")
    logging.info(f"Client disconnected: {websocket.remote_address} ({username}). Total clients: {len(connected_clients)}")
    
    # Notify all clients that a user has left
    leave_message = {
        "type": "user_left",
        "username": username,
        "timestamp": int(time.time() * 1000) # Milliseconds timestamp
    }
    await broadcast_message(json.dumps(leave_message))
    
    # Send updated user list to all clients
    await send_active_users_list()

async def handle_message(websocket):
    """
    Handles incoming messages from a client, determines their type, and processes them.
    """
    username = None # Will be set on the first message (registration)
    try:
        async for message in websocket:
            logging.info(f"Received message from {websocket.remote_address}: {message}")
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "register":
                    # This is the initial message from the client to set their username
                    # We expect 'username' in this message
                    if "username" in data and not username: # Only register once
                        username = data["username"]
                        await register(websocket, username)
                    else:
                        logging.warning(f"Invalid or duplicate registration attempt from {websocket.remote_address}: {message}")
                    continue # Do not process as a chat message

                if not username:
                    logging.warning(f"Unregistered client sent message: {websocket.remote_address} - {message}")
                    continue # Ignore messages from unregistered clients

                # Add timestamp to all outgoing messages (if not already present)
                if "timestamp" not in data:
                    data["timestamp"] = int(time.time() * 1000) # Milliseconds timestamp
                
                if msg_type == "chat_message":
                    # Public message
                    if "text" in data:
                        data["username"] = username # Ensure correct sender username
                        await broadcast_message(json.dumps(data), exclude_websocket=websocket)
                    else:
                        logging.warning(f"Invalid chat_message format from {username}: {message}")
                
                elif msg_type == "private_message":
                    # Private message
                    recipient_username = data.get("recipient")
                    message_text = data.get("text")
                    if recipient_username and message_text:
                        recipient_ws = None
                        for ws_client, user in connected_clients.items():
                            if user == recipient_username:
                                recipient_ws = ws_client
                                break
                        
                        if recipient_ws:
                            # Send to recipient
                            data["username"] = username # Sender
                            data["is_private"] = True # Mark as private
                            await recipient_ws.send(json.dumps(data))
                            
                            # Optionally, send a copy back to the sender for their own chat history
                            # data["is_sent_private"] = True # Mark as sent private
                            # await websocket.send(json.dumps(data))
                            logging.info(f"Private message from {username} to {recipient_username}: {message_text}")
                        else:
                            # Notify sender if recipient is not found
                            error_message = {
                                "type": "system_message",
                                "text": f"User '{recipient_username}' not found or offline.",
                                "timestamp": int(time.time() * 1000)
                            }
                            await websocket.send(json.dumps(error_message))
                            logging.warning(f"Private message failed: Recipient '{recipient_username}' not found.")
                    else:
                        logging.warning(f"Invalid private_message format from {username}: {message}")

                elif msg_type == "typing_status":
                    # Typing status update
                    is_typing = data.get("is_typing")
                    recipient = data.get("recipient") # Check if it's for a private chat

                    typing_status_message = {
                        "type": "typing_status",
                        "username": username, # The user who is typing
                        "is_typing": is_typing
                    }

                    if recipient:
                        # If it's a private typing status, send only to the recipient
                        recipient_ws = None
                        for ws_client, user in connected_clients.items():
                            if user == recipient:
                                recipient_ws = ws_client
                                break
                        if recipient_ws:
                            try:
                                await recipient_ws.send(json.dumps(typing_status_message))
                                logging.info(f"Private typing status from {username} to {recipient}: {is_typing}")
                            except websockets.exceptions.ConnectionClosedOK:
                                logging.warning(f"Failed to send private typing status to disconnected client: {recipient}")
                        else:
                            logging.warning(f"Private typing status failed: Recipient '{recipient}' not found.")
                    else:
                        # If no recipient, it's a public typing status, broadcast to all others
                        await broadcast_message(json.dumps(typing_status_message), exclude_websocket=websocket)
                        logging.info(f"Public typing status from {username}: {is_typing}")

                else:
                    logging.warning(f"Unknown message type from {username}: {msg_type} - {message}")

            except json.JSONDecodeError:
                logging.error(f"Failed to decode JSON message from {websocket.remote_address}: {message}")
            except Exception as e:
                logging.error(f"Error processing message from {websocket.remote_address}: {e}")
    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"Connection closed normally by {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed with error by {websocket.remote_address}: {e}")
    except Exception as e:
        logging.critical(f"Unexpected error in handle_message for {websocket.remote_address}: {e}")
    finally:
        if websocket in connected_clients: # Ensure cleanup only if registered
            await unregister(websocket)

async def main():
    """Starts the WebSocket server."""
    server_address = "localhost"
    server_port = 8765
    async with websockets.serve(handle_message, server_address, server_port):
        logging.info(f"WebSocket server started on ws://{server_address}:{server_port}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logging.critical(f"Server encountered a critical error: {e}")
