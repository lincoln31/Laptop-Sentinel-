# 👁️ Laptop Sentinel

**Turn your laptop's webcam into a private, on-demand security camera. Simple, secure, and self-hosted.**

[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

### The "Why": A Real-World Solution

Professional security cameras can be expensive, and sometimes you just need a simple way to keep an eye on your space. I created Vigilante because I needed a security solution without the high cost. My laptop is almost always on, so why not use its webcam?

Vigilante was born from this idea: to provide a free, private, and easy-to-use security camera system that you control completely. Before leaving home, you can activate the stream and have a live video feed of your entrance, your room, or any space you want to monitor, right from your phone. It gives you peace of mind, affordably.

### Features

-   **Live Video Streaming:** Access a real-time video feed from your webcam in any browser.
-   **On-Demand Recording:** Start and stop video recordings with a single click.
-   **Secure Access:** Protected by a unique, auto-generated token. Only you can access the feed.
-   **Self-Hosted & Private:** Your video data never leaves your network unless you choose to expose it. No cloud, no subscriptions.
-   **Easy Deployment:** Runs inside a Docker container, making setup incredibly simple on any OS.
-   **Responsive UI:** A clean and modern web interface to view the stream and control recordings.

### Tech Stack

-   **Backend:** Python with Flask
-   **Video Processing:** OpenCV
-   **Containerization:** Docker & Docker Compose
-   **Frontend:** HTML, CSS, Vanilla JavaScript

### Getting Started

#### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
-   A computer with a webcam.
-   (Optional) A VPN service like [Tailscale](https://tailscale.com/) for easy access from outside your home network.

#### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/lincoln31/Laptop-Sentinel-.git
    cd laptop-Sentinel
    ```

2.  **(Optional) Configure Tailscale IP:**
    If you want to access the camera from anywhere using Tailscale, open the `docker-compose.yml` file and set your Tailscale IP address:
    ```yaml
    environment:
      - PYTHONUNBUFFERED=1
      # Add your Tailscale IP here
      - TAILSCALE_IP=100.x.x.x 
    ```

3.  **Build and run the application:**
    This command will build the Docker image and start the application in the background.
    ```bash
    docker compose up --build -d
    ```
    *(The `-d` flag runs it in detached mode)*

4.  **Get your access token:**
    The application generates a unique, secret token on startup. To get it, view the container's logs:
    ```bash
    docker logs camera_streaming_app
    ```
    You will see a message like this. **Copy the token!**
    ```
    ==================================================
    ✅ ¡APLICACIÓN LISTA! ACCEDE DESDE LAS SIGUIENTES URLS:
    ==================================================
    🏠 Local: http://localhost:5000/?token=A_VERY_SECRET_TOKEN_HERE
    🌍 Tailscale: http://100.x.x.x:5000/?token=A_VERY_SECRET_TOKEN_HERE
    ==================================================
    ```

5.  **Access Vigilante:**
    Open your browser and navigate to the URL shown in the logs (e.g., `http://localhost:5000/?token=YOUR_SECRET_TOKEN`). You should now see the live video stream!

### How to Use

-   **View Stream:** The video feed is shown on the main page.
-   **Start Recording:** Click the "Iniciar Grabación" button. A "REC" indicator will appear on the video.
-   **Stop Recording:** Click the "Detener Grabación" button. The video file will be saved.
-   **View Recordings:** Click "Ver Grabaciones" to see a list of all saved video files, along with their size and creation date. All recordings are stored in the `recordings` folder on your host machine.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
