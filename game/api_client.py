import requests
import time

BASE_URL = "http://127.0.0.1:5000"


def start_session(user_id):
    try:
        response = requests.post(
            f"{BASE_URL}/api/start_session",
            json={"user_id": user_id}
        )
        data = response.json()
        return data.get("session_id")
    except Exception as e:
        print("Error start_session:", e)
        return None
    
def get_active_user():
    for _ in range(3):  # Coba hingga 3 kali
        try:
            response = requests.get(f"{BASE_URL}/api/get_active_user")
            data = response.json()

            if data["status"] == "success":
                return data["user"]
        except Exception as e:
            print("Error get_active_user:", e)
            time.sleep(1)  # Tunggu 1 detik sebelum coba lagi
    return None

def end_session(session_id, skor):
    try:
        requests.post(
            f"{BASE_URL}/api/end_session",
            json={
                "session_id": session_id,
                "skor": skor
            }
        )
    except Exception as e:
        print("Error end_session:", e)