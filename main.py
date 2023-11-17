import requests
import dotenv
import os
import time
import argparse


def get_arguments() -> dict:
    parser = argparse.ArgumentParser(description="Automatic message sender")

    parser.add_argument(
        "-r",
        "--RoomId",
        help="Room Id (right click on room or profile with discord developper mode ON)",
    )
    parser.add_argument(
        "-m",
        "--Message",
        help="The message to send",
    )
    parser.add_argument("-l", "--Loop", help="Number of messages to send", type=int)
    parser.add_argument(
        "-d", "--Delay", help="Delay in seconds between each seocnd", type=int
    )

    args = parser.parse_args()

    values = {}
    if args.RoomId:
        values["room_id"] = args.RoomId
    if args.Message:
        values["message"] = args.Message
    if args.Loop:
        values["loop"] = args.Loop
    if args.Delay:
        values["delay"] = args.Delay

    return values


def load_env(path: str) -> None:
    if not dotenv.load_dotenv(path):
        raise Exception(f"Could not load '{path}'")


def get_token() -> str:
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise ValueError("Could not find DISCORD_TOKEN key in env")

    return token


def get_input(prompt: str, wrapper, error: str = "Please enter a valid string"):
    try:
        value = wrapper(input(prompt))
    except ValueError:
        print(error)
        return get_input(prompt, error)
    return value


def send(token: str, url: str, payload: dict, index: int) -> bool:
    res = requests.post(url, data=payload, headers={"authorization": token})
    status = res.status_code

    if status != 200:
        extra = ""
        if status == 401:
            extra = "Token might be invalid"

        print(
            f"[{status}] Failed to send message{f': {extra}' if extra else ''}",
        )
        return False

    return True


def main() -> None:
    load_env(".env")
    token = get_token()

    args = get_arguments()

    room_id = args["room_id"] if "room_id" in args else get_input("Room id >> ", str)
    message = args["message"] if "message" in args else get_input("Message >> ", str)
    loop = args["loop"] if "loop" in args else get_input("Loop >> ", int)
    delay = args["delay"] if "delay" in args else get_input("Delay (s) >> ", int)

    url = f"https://discord.com/api/v8/channels/{room_id}/messages"
    payload = {"content": message}
    failed_attempts = 0

    for i in range(1, loop + 1):
        time.sleep(delay)
        print(f'Sending "{message}" №{i} of {loop}')

        success = send(token, url, payload, i)

        if not success:
            failed_attempts += 1

        if failed_attempts >= 3:
            print("Reached max failed attempts (3), stopping...")
            exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting")
        exit(0)
