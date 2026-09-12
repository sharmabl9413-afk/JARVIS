from flask import Flask, request, jsonify
import subprocess
import webbrowser
import pyautogui
import os

app = Flask(__name__)


@app.route("/")
def home():

    return jsonify({
        "jarvis": "online"
    })


@app.route("/open_url", methods=["POST"])
def open_url():

    data = request.json

    url = data.get("url")

    if not url:
        return jsonify({
            "success": False
        })

    webbrowser.open(url)

    return jsonify({
        "success": True
    })


@app.route("/open_app", methods=["POST"])
def open_app():

    data = request.json

    app_name = data.get("app", "").lower()

    try:

        if app_name == "chrome":

            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]

            for path in possible_paths:

                if os.path.exists(path):

                    subprocess.Popen([path])

                    return jsonify({
                        "success": True
                    })

        return jsonify({
            "success": False,
            "error": "Application not found"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/volume", methods=["POST"])
def volume():

    data = request.json

    action = data.get("action")

    if action == "up":

        pyautogui.press("volumeup")

    elif action == "down":

        pyautogui.press("volumedown")

    return jsonify({
        "success": True
    })


@app.route("/mouse", methods=["POST"])
def mouse():

    data = request.json

    x = data.get("x")
    y = data.get("y")

    if x is not None and y is not None:

        pyautogui.moveTo(
            int(x),
            int(y),
            duration=0.2
        )

    return jsonify({
        "success": True
    })


@app.route("/click", methods=["POST"])
def click():

    pyautogui.click()

    return jsonify({
        "success": True
    })


@app.route("/type", methods=["POST"])
def type_text():

    data = request.json

    text = data.get("text", "")

    pyautogui.write(
        text,
        interval=0.01
    )

    return jsonify({
        "success": True
    })


@app.route("/lock", methods=["POST"])
def lock():

    os.system(
        "rundll32.exe user32.dll,LockWorkStation"
    )

    return jsonify({
        "success": True
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
