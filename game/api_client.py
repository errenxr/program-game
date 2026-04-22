import requests
import time

BASE_URL = "http://127.0.0.1:5000"

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


def get_active_anak():
    for _ in range(3):  # retry
        try:
            response = requests.get(f"{BASE_URL}/api/get_active_anak")
            data = response.json()

            if data.get("status") == "success":
                return data.get("anak")

        except Exception as e:
            print("Error get_active_anak:", e)
            time.sleep(1)

    return None

# ================= END SESSION =================
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