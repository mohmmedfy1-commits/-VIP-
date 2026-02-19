import flet as ft
import subprocess
import json
import os
from pyzbar.pyzbar import decode
from PIL import Image

XRAY_PATH = "xray/xray"
CONFIG_PATH = "xray/config.json"

PASSWORD = "1234"

xray_process = None


def start_vpn():
    global xray_process

    if xray_process is None:
        xray_process = subprocess.Popen(
            [XRAY_PATH, "-config", CONFIG_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


def stop_vpn():
    global xray_process

    if xray_process:
        xray_process.kill()
        xray_process = None


def import_config_from_qr(image_path):

    img = Image.open(image_path)
    result = decode(img)

    if result:
        config = result[0].data.decode()

        with open(CONFIG_PATH, "w") as f:
            f.write(config)

        return True

    return False


def main(page: ft.Page):

    page.title = "XRAY VPN"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    status = ft.Text("Disconnected", size=20)

    password_input = ft.TextField(
        label="Password",
        password=True
    )

    def connect(e):

        if password_input.value != PASSWORD:
            status.value = "Wrong Password"
            page.update()
            return

        start_vpn()
        status.value = "Connected"
        page.update()

    def disconnect(e):
        stop_vpn()
        status.value = "Disconnected"
        page.update()

    file_picker = ft.FilePicker()

    def pick_file_result(e):

        if e.files:

            path = e.files[0].path

            if import_config_from_qr(path):
                status.value = "Config Imported"
            else:
                status.value = "Import Failed"

            page.update()

    file_picker.on_result = pick_file_result

    page.overlay.append(file_picker)

    page.add(
        ft.Column(
            [
                ft.Text("XRAY VPN", size=30),

                password_input,

                ft.ElevatedButton(
                    "Connect VPN",
                    on_click=connect
                ),

                ft.ElevatedButton(
                    "Disconnect VPN",
                    on_click=disconnect
                ),

                ft.ElevatedButton(
                    "Import via QR",
                    on_click=lambda e: file_picker.pick_files()
                ),

                status
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )


ft.app(target=main)
