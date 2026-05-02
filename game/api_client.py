import requests
import time

BASE_URL = "http://10.193.182.65:5000"

def start_session(anak_id):
    try:
        response = requests.post(
            f"{BASE_URL}/api/start_session",
            json={"anak_id": anak_id}
        )
        data = response.json()
        return data.get("session_id")
    except Exception as e:
        print("Error start_session:", e)
        return None


def get_active_anak(user_id):
    for _ in range(3):
        try:
            response = requests.get(f"{BASE_URL}/api/get_active_anak", params={"user_id": user_id})
            data = response.json()

            if data.get("status") == "success":
                return data.get("anak")

        except Exception as e:
            print("Error get_active_anak:", e)
            time.sleep(1)

    return None

def get_current_user():
    try:
        response = requests.get(f"{BASE_URL}/api/get_current_user")
        data = response.json()

        if data.get("status") == "success":
            return data.get("user_id")
    except Exception as e:
        print("Error get_current_user:", e)

    return None

def end_session(session_id, skor, current_level):
    try:
        requests.post(
            f"{BASE_URL}/api/end_session",
            json={
                "session_id": session_id,
                "skor": skor,
                "level": current_level
            }
        )
    except Exception as e:
        print("Error end_session:", e)

def update_level(anak_id, level):
    try:
        requests.post(
            f"{BASE_URL}/api/update_level",
            json={
                "anak_id": anak_id,
                "level": level
            }
        )
    except Exception as e:
        print("Error update_level:", e)