import base64
from io import BytesIO
from matrix_client.api import MatrixHttpApi
import subprocess
from .templates import format

token = subprocess.check_output(["pass", "matrix"]).decode("utf-8").strip()
channel_real = subprocess.check_output(["pass", "matrix-imma-channel-real"]).decode("utf-8").strip()
channel_test = subprocess.check_output(["pass", "matrix-imma-channel"]).decode("utf-8").strip()

matrix = MatrixHttpApi("https://matrix.org", token=token)



def publish(data, test=True):
    message = format(data, test)['body']

    room = get_a_room(data["parse"]["event_id"], test)
        
    matrix.send_message(room, message)

    for section in ['integralallsky', 'ivis']:
        if section in data:
            for k, v in data[section].items():
                if k.endswith("_content"):
                    uploaded = matrix.media_upload(BytesIO(base64.b64decode(v)), "image/png", k)
                    print(uploaded)
                    matrix.send_content(room, uploaded['content_uri'], k, "m.image")


def get_a_room(event_id, test=True):
    if test:
        from_channel = channel_test
    else:
        from_channel = channel_real

    print("from channel", from_channel)

    room_alias = f'INTEGRAL-{event_id}'
    if test:
        room_alias += "-test"

    print("room alias", room_alias)



    try:
        room = matrix.create_room(room_alias)['room_id']
    except Exception as e:
        print("failed to create room due to", e)
        room = f"#{room_alias}:matrix.org"
    
    try:
        room = matrix.join_room(room)['room_id']
        print("room join", room)
    except Exception as e:
        print("failed to join room due to", e)


    try:
        channel_members = matrix.get_room_members(from_channel)
        print("members", channel_members)

        for user in channel_members['chunk']:
            if user['content']['membership'] == 'join':
                print("invite", user)
                try:
                    print(matrix.invite_user(room, user['user_id']))
                except Exception as e:
                    print("failed to invite user", user, "due to", e)

    except Exception as e:
        print("failed to get members due to", e)

    # set_join_rule
    
    return room


def cleanup():
    for room in matrix.list_joined_rooms():
        try:
            print(room, matrix.get_room_name(room))
        except Exception as e:
            print(room, "failed to get room name due to", e)
            # print(matrix.get_room_messages(room, "", "b"))
            print(matrix.get_room_aliases(room))
            continue