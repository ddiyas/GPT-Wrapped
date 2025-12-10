from datetime import datetime


def extract_messages(conversation):
    messages = []
    current_node = conversation.get("current_node")
    mapping = conversation.get("mapping", {})

    if not current_node or not mapping:
        return messages

    while current_node is not None:
        node = mapping.get(current_node)
        if not node:
            break

        message = node.get("message")
        if (
            message
            and message.get("content")
            and message.get("content", {}).get("parts")
        ):
            parts_list = message.get("content", {}).get("parts", [])
            if len(parts_list) > 0:
                author = message.get("author", {}).get("role", "")
                is_user_system = message.get("metadata", {}).get(
                    "is_user_system_message", False
                )

                if author != "system" or is_user_system:
                    if author == "assistant" or author == "tool":
                        author = "ChatGPT"
                    elif author == "system" and is_user_system:
                        author = "Custom user info"

                    content_type = message.get("content", {}).get("content_type", "")
                    if content_type in ["text", "multimodal_text"]:
                        parts = []
                        for part in parts_list:
                            if isinstance(part, str) and len(part) > 0:
                                parts.append({"text": part})
                            elif isinstance(part, dict):
                                part_content_type = part.get("content_type", "")
                                if part_content_type == "audio_transcription":
                                    parts.append({"transcript": part.get("text")})
                                elif part_content_type in [
                                    "audio_asset_pointer",
                                    "image_asset_pointer",
                                    "video_container_asset_pointer",
                                ]:
                                    parts.append({"asset": part})
                                elif (
                                    part_content_type
                                    == "real_time_user_audio_video_asset_pointer"
                                ):
                                    if part.get("audio_asset_pointer"):
                                        parts.append(
                                            {"asset": part.get("audio_asset_pointer")}
                                        )
                                    if part.get("video_container_asset_pointer"):
                                        parts.append(
                                            {
                                                "asset": part.get(
                                                    "video_container_asset_pointer"
                                                )
                                            }
                                        )
                                    for frame in part.get("frames_asset_pointers", []):
                                        parts.append({"asset": frame})

                        if len(parts) > 0:
                            messages.append(
                                {
                                    "author": author,
                                    "parts": parts,
                                    "timestamp": message.get("create_time"),
                                }
                            )

        current_node = node.get("parent")

    return list(reversed(messages))


def filter_messages_by_year(messages, year):
    filtered = []
    for msg in messages:
        if "timestamp" in msg and msg["timestamp"]:
            try:
                timestamp = datetime.fromtimestamp(msg["timestamp"])
                if timestamp.year == year:
                    filtered.append(msg)
            except:
                pass
    return filtered
